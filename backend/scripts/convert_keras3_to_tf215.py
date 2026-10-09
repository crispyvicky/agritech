"""Convert Keras 3 .keras archives to a TF/Keras 2.15-loadable .keras zip."""
import json
import shutil
import zipfile
from pathlib import Path

import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


def convert_dtype(dtype):
    if isinstance(dtype, dict):
        return dtype.get("config", {}).get("name", "float32")
    return dtype


def convert_inbound(nodes):
    if not nodes:
        return []
    converted = []
    for node in nodes:
        if isinstance(node, dict) and "args" in node:
            args = node.get("args", [])
            kwargs = node.get("kwargs", {}) or {}
            tensors = []

            def collect(a):
                if isinstance(a, dict) and a.get("class_name") == "__keras_tensor__":
                    hist = a["config"].get("keras_history", [])
                    if hist:
                        tensors.append(hist)
                elif isinstance(a, list):
                    for x in a:
                        collect(x)

            for a in args:
                collect(a)

            inbound = []
            for hist in tensors:
                if len(hist) >= 3:
                    inbound.append([hist[0], hist[1], hist[2], kwargs if kwargs else {}])
            if inbound:
                converted.append(inbound)
        elif isinstance(node, list):
            converted.append(node)
    return converted


def convert_layer(layer):
    l = dict(layer)
    l["module"] = "keras.layers"
    cfg = dict(l.get("config") or {})

    if l.get("class_name") == "InputLayer":
        if "batch_shape" in cfg:
            bs = cfg.pop("batch_shape")
            cfg["batch_input_shape"] = bs
            if bs and len(bs) > 1:
                cfg["input_shape"] = bs[1:]

    if "dtype" in cfg:
        cfg["dtype"] = convert_dtype(cfg["dtype"])

    cfg.pop("quantization_config", None)
    l["config"] = cfg
    l["inbound_nodes"] = convert_inbound(l.get("inbound_nodes") or [])
    l.pop("build_config", None)
    l.pop("registered_name", None)
    return l


def convert_config(cfg):
    layers = [convert_layer(l) for l in cfg["config"]["layers"]]
    inputs = [l["name"] for l in layers if l["class_name"] == "InputLayer"]

    referenced = set()
    for l in layers:
        for node in l.get("inbound_nodes") or []:
            for ref in node:
                if isinstance(ref, list) and ref:
                    referenced.add(ref[0])

    outputs = [
        l["name"]
        for l in layers
        if l["name"] not in referenced and l["class_name"] != "InputLayer"
    ]
    if not outputs:
        outputs = [layers[-1]["name"]]

    return {
        "class_name": "Functional",
        "config": {
            "name": cfg["config"].get("name", "model"),
            "layers": layers,
            "input_layers": [[n, 0, 0] for n in inputs],
            "output_layers": [[outputs[-1], 0, 0]],
        },
    }


def convert_model(src: Path, dst: Path) -> None:
    tmpdir = dst.parent / f"_convert_{dst.stem}"
    if tmpdir.exists():
        shutil.rmtree(tmpdir)
    tmpdir.mkdir()

    with zipfile.ZipFile(src) as z:
        z.extractall(tmpdir)

    cfg = json.loads((tmpdir / "config.json").read_text(encoding="utf-8"))
    new_cfg = convert_config(cfg)
    (tmpdir / "config.json").write_text(json.dumps(new_cfg), encoding="utf-8")
    (tmpdir / "metadata.json").write_text(
        json.dumps({"keras_version": "2.15.0"}), encoding="utf-8"
    )

    if dst.exists():
        dst.unlink()
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in tmpdir.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(tmpdir).as_posix())

    shutil.rmtree(tmpdir, ignore_errors=True)
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")


def try_load(path: Path):
    import tensorflow as tf

    try:
        m = tf.keras.models.load_model(path, compile=False)
        print("LOAD OK", path.name, m.input_shape, m.output_shape)
        return True
    except Exception as e:
        print("LOAD FAIL", path.name, type(e).__name__, str(e)[:400])
        return False


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "models"
    pairs = [
        (root / "best_plantdoc_model.keras", root / "plantdoc_tf215.keras"),
        (root / "soil_classifier.keras", root / "soil_tf215.keras"),
        (root / "soil_classifier_fallback.keras", root / "soil_fallback_tf215.keras"),
    ]
    for src, dst in pairs:
        if not src.exists():
            print("missing", src)
            continue
        convert_model(src, dst)
        try_load(dst)
