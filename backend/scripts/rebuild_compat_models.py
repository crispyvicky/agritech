"""Rebuild Keras-3 PlantDoc/Soil models on TF 2.15 with exact preprocessing."""
import json
import os
import zipfile
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import cv2
import h5py
import numpy as np
import tensorflow as tf
from tensorflow.keras import Model, Sequential, layers
from tensorflow.keras.applications import EfficientNetB4

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"

WEIGHT_CLASSES = {
    "Conv2D",
    "DepthwiseConv2D",
    "Dense",
    "BatchNormalization",
    "Normalization",
}


def extract_archive(src_keras: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src_keras) as z:
        z.extractall(out_dir)
    cfg = json.loads((out_dir / "config.json").read_text(encoding="utf-8"))
    return cfg, out_dir / "model.weights.h5"


def h5_layers_by_class(weights_path: Path):
    buckets = defaultdict(list)
    with h5py.File(weights_path, "r") as f:
        for name in f["layers"].keys():
            group = f["layers"][name]
            if "vars" not in group or len(group["vars"]) == 0:
                continue
            arrays = [
                group["vars"][k][()]
                for k in sorted(group["vars"].keys(), key=lambda x: int(x))
            ]
            if name.startswith("depthwise_conv2d"):
                cls = "DepthwiseConv2D"
            elif name.startswith("conv2d"):
                cls = "Conv2D"
            elif name.startswith("batch_normalization"):
                cls = "BatchNormalization"
            elif name.startswith("dense"):
                cls = "Dense"
            elif name == "normalization" or name.startswith("normalization_"):
                cls = "Normalization"
            else:
                continue
            buckets[cls].append((name, arrays))

    def sort_key(item):
        name = item[0]
        parts = name.split("_")
        tail = parts[-1]
        base = name if not tail.isdigit() else "_".join(parts[:-1])
        idx = int(tail) if tail.isdigit() else -1
        return base, idx

    for cls in buckets:
        buckets[cls] = sorted(buckets[cls], key=sort_key)
    return buckets


def load_by_config_order(model: Model, cfg: dict, weights_path: Path) -> int:
    buckets = h5_layers_by_class(weights_path)
    cursors = defaultdict(int)
    loaded = 0

    for layer_cfg in cfg["config"]["layers"]:
        cls = layer_cfg.get("class_name")
        name = layer_cfg.get("name")
        if cls not in WEIGHT_CLASSES:
            continue
        try:
            layer = model.get_layer(name)
        except ValueError:
            continue
        if not layer.weights:
            continue
        if cursors[cls] >= len(buckets[cls]):
            print("exhausted", cls, "at", name)
            continue

        h5_name, arrays = buckets[cls][cursors[cls]]
        expected = layer.get_weights()

        if len(arrays) != len(expected) or any(a.shape != e.shape for a, e in zip(arrays, expected)):
            found = False
            for j in range(cursors[cls], len(buckets[cls])):
                alt_name, alt = buckets[cls][j]
                if len(alt) == len(expected) and all(a.shape == e.shape for a, e in zip(alt, expected)):
                    arrays = alt
                    buckets[cls][cursors[cls]], buckets[cls][j] = buckets[cls][j], buckets[cls][cursors[cls]]
                    found = True
                    break
            if not found:
                print("mismatch", name, "<-", h5_name, [a.shape for a in arrays], [e.shape for e in expected])
                continue

        # Keep Normalization variance as stored in archive (std values). Combined with
        # rescaling_1(scale=1/sqrt(std)) this matches training.
        layer.set_weights(arrays)
        cursors[cls] += 1
        loaded += 1

    print(f"loaded {loaded} layers")
    return loaded


def build_plantdoc_model(cfg: dict) -> Model:
    """EfficientNetB4 backbone from stem onward + exact saved preprocessing + head."""
    # Template for layer reuse (includes unused default preprocessing layers)
    template = EfficientNetB4(include_top=False, weights=None, input_shape=(224, 224, 3))

    # Exact preprocessing from saved config
    scales = None
    for layer_cfg in cfg["config"]["layers"]:
        if layer_cfg.get("name") == "rescaling_1":
            scales = layer_cfg["config"]["scale"]
            break
    if scales is None:
        scales = [2.0896918976428642, 2.1128856368212916, 2.1081851067789197]

    inp = layers.Input(shape=(224, 224, 3), name="input_layer")
    x = layers.Rescaling(1.0 / 255.0, name="rescaling")(inp)
    x = layers.Normalization(axis=3, name="normalization")(x)
    x = layers.Rescaling(scales, name="rescaling_1")(x)

    # Reuse EfficientNet layers starting at stem_conv_pad (skip template prep)
    started = False
    for layer in template.layers:
        if layer.name == "stem_conv_pad":
            started = True
        if not started:
            continue
        x = layer(x)

    y = layers.GlobalAveragePooling2D(name="global_average_pooling2d")(x)
    y = layers.Dense(1024, activation="relu", name="dense")(y)
    y = layers.BatchNormalization(name="batch_normalization")(y)
    y = layers.Dropout(0.5, name="dropout")(y)
    y = layers.Dense(512, activation="relu", name="dense_1")(y)
    y = layers.BatchNormalization(name="batch_normalization_1")(y)
    y = layers.Dropout(0.5, name="dropout_1")(y)
    out = layers.Dense(27, activation="softmax", name="dense_2")(y)
    return Model(inp, out, name="plantdoc_compat")


def build_soil_model() -> Model:
    return Sequential(
        [
            layers.Input(shape=(180, 180, 3)),
            layers.Rescaling(1.0 / 255.0),
            layers.Conv2D(32, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(256, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(4, activation="softmax"),
        ],
        name="soil_compat",
    )


def load_soil_weights(model: Model, weights_path: Path) -> int:
    buckets = h5_layers_by_class(weights_path)
    print("soil h5 conv", [a[0].shape for _, a in buckets["Conv2D"]])
    print("soil h5 dense", [a[0].shape for _, a in buckets["Dense"]])
    cursors = defaultdict(int)
    loaded = 0
    class_map = {
        layers.Conv2D: "Conv2D",
        layers.Dense: "Dense",
        layers.BatchNormalization: "BatchNormalization",
    }
    for layer in model.layers:
        cls = next((v for k, v in class_map.items() if isinstance(layer, k)), None)
        if cls is None or not layer.weights:
            continue
        expected = layer.get_weights()
        for j in range(cursors[cls], len(buckets[cls])):
            h5_name, arrays = buckets[cls][j]
            if len(arrays) == len(expected) and all(a.shape == e.shape for a, e in zip(arrays, expected)):
                layer.set_weights(arrays)
                buckets[cls][cursors[cls]], buckets[cls][j] = buckets[cls][j], buckets[cls][cursors[cls]]
                cursors[cls] += 1
                loaded += 1
                break
        else:
            print("no match for", layer.name, [e.shape for e in expected])
    print("soil loaded", loaded)
    return loaded


def evaluate_plant(model: Model):
    names = json.loads((MODELS / "plantdoc_class_names.json").read_text(encoding="utf-8"))
    samples = [
        ROOT / "PlantDoc-Dataset" / "test" / "Apple leaf" / "Apple leaf (4).jpg",
        ROOT / "PlantDoc-Dataset" / "test" / "Tomato leaf late blight" / "Tomato leaf late blight (1).jpg",
        ROOT / "PlantDoc-Dataset" / "test" / "Corn rust leaf" / "Corn rust leaf (1).jpg",
    ]
    for path in samples:
        if not path.exists():
            print("missing", path)
            continue
        img = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224)).astype("float32")
        pred = model.predict(np.expand_dims(img, 0), verbose=0)[0]
        top = sorted([(names[i], float(pred[i])) for i in range(len(pred))], key=lambda x: -x[1])[:3]
        print(path.parent.name, "->", top)


def main():
    plant_cfg, plant_w = extract_archive(MODELS / "best_plantdoc_model.keras", MODELS / "_weights_plantdoc")
    plant = build_plantdoc_model(plant_cfg)
    print("layers", len(plant.layers), "weight layers", sum(1 for l in plant.layers if l.weights))
    load_by_config_order(plant, plant_cfg, plant_w)
    evaluate_plant(plant)
    out = MODELS / "plantdoc_compat.keras"
    plant.save(out)
    print("saved", out)

    soil_cfg, soil_w = extract_archive(MODELS / "soil_classifier.keras", MODELS / "_weights_soil")
    soil = build_soil_model()
    # Build once to know flatten size; if dense mismatch, rebuild using h5 dense in-shape
    load_soil_weights(soil, soil_w)
    # If dense not loaded, rebuild with correct flatten via known weight shape
    buckets = h5_layers_by_class(soil_w)
    dense_in = buckets["Dense"][0][1][0].shape[0]
    if soil.layers[-3].weights and soil.layers[-3].get_weights()[0].shape[0] != dense_in:
        print("rebuilding soil for flatten", dense_in)
    # Force correct architecture with GlobalAveragePooling if needed? Prefer match flatten.
    # Compute spatial size: for 180 input with 4x MaxPool(2) and valid conv3: 
    # Use a model that matches 30976 = 256 * 121 => 11*11*256
    soil = Sequential(
        [
            layers.Input(shape=(180, 180, 3)),
            layers.Rescaling(1.0 / 255.0),
            layers.Conv2D(32, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(256, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(4, activation="softmax"),
        ],
        name="soil_compat",
    )
    # Probe flatten size
    probe = soil.predict(np.zeros((1, 180, 180, 3), dtype="float32"), verbose=0)
    flat = soil.layers[-3].input_shape
    print("soil flatten input", getattr(soil.layers[-2], "input_shape", None), "dense in h5", dense_in)
    # Manually set by building intermediate
    x = np.zeros((1, 180, 180, 3), dtype="float32")
    tmp = Model(soil.input, soil.layers[-4].output)  # before flatten? 
    # easier: iterate
    from tensorflow.keras import backend as K
    feat = soil.layers[0](x) if False else None

    # Build with explicit same padding to hit 11x11
    soil = Sequential(
        [
            layers.Input(shape=(180, 180, 3)),
            layers.Rescaling(1.0 / 255.0),
            layers.Conv2D(32, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Conv2D(256, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(4, activation="softmax"),
        ],
        name="soil_compat",
    )
    _ = soil(np.zeros((1, 180, 180, 3), dtype="float32"))
    print("same-pad dense kernel want", soil.get_layer(index=10).kernel.shape, "h5", buckets["Dense"][0][1][0].shape)
    load_soil_weights(soil, soil_w)
    print("soil smoke", soil.predict(np.random.rand(1, 180, 180, 3).astype("float32") * 255, verbose=0)[0])
    soil_out = MODELS / "soil_compat.keras"
    soil.save(soil_out)
    print("saved", soil_out)


if __name__ == "__main__":
    main()
