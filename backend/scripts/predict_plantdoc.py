"""
Plant disease prediction.

Primary: EfficientNetB0 (ImageNet) embeddings + nearest class from PlantDoc images.
This is reliable for demos when the fine-tuned .keras head is low-quality/incompatible.
Optional: Keras3+Torch worker for the original model when confidence is high.
"""
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CLASS_PATH = ROOT / "models" / "plantdoc_class_names.json"
CACHE_PATH = ROOT / "models" / "plantdoc_embed_index.npz"
DATA_DIRS = [
    ROOT / "PlantDoc-Dataset" / "test",
    ROOT / "PlantDoc-Dataset" / "train",
]
WORKER = ROOT / "scripts" / "plant_predict_worker.py"
WORKER_PY = ROOT / ".venv_plant" / "Scripts" / "python.exe"

_embed_model = None
_index = None  # dict class -> mean embedding
_class_names = None

HEALTHY = {
    "Apple leaf", "Bell_pepper leaf", "Blueberry leaf", "Cherry leaf", "grape leaf",
    "Peach leaf", "Raspberry leaf", "Soyabean leaf", "Strawberry leaf", "Tomato leaf",
}


def load_class_names():
    global _class_names
    if _class_names is None:
        if CLASS_PATH.exists():
            _class_names = json.loads(CLASS_PATH.read_text(encoding="utf-8"))
        else:
            _class_names = sorted(
                d.name for d in (ROOT / "PlantDoc-Dataset" / "test").iterdir() if d.is_dir()
            )
    return _class_names


def get_healthy_classes():
    return HEALTHY


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        import tensorflow as tf
        from tensorflow.keras.applications import EfficientNetB0

        logger.info("Loading EfficientNetB0 ImageNet embedder for plant matching...")
        _embed_model = EfficientNetB0(
            include_top=False, weights="imagenet", pooling="avg", input_shape=(224, 224, 3)
        )
    return _embed_model


def _preprocess(img_bgr_or_rgb, is_bgr=True):
    from tensorflow.keras.applications.efficientnet import preprocess_input

    img = img_bgr_or_rgb
    if is_bgr:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224)).astype("float32")
    return preprocess_input(np.expand_dims(img, 0))


def _embed_path(path: Path):
    img = cv2.imread(str(path))
    if img is None:
        return None
    model = _get_embed_model()
    vec = model.predict(_preprocess(img), verbose=0)[0]
    n = np.linalg.norm(vec) + 1e-8
    return (vec / n).astype("float32")


def _build_or_load_index(max_per_class=8):
    global _index
    if _index is not None:
        return _index

    if CACHE_PATH.exists():
        try:
            data = np.load(CACHE_PATH, allow_pickle=True)
            labels = list(data["labels"])
            vectors = data["vectors"]
            _index = {lab: vectors[i] for i, lab in enumerate(labels)}
            logger.info(f"Loaded plant embed index ({len(_index)} classes)")
            return _index
        except Exception as e:
            logger.warning(f"Embed cache load failed: {e}")

    data_root = next((d for d in DATA_DIRS if d.exists()), None)
    if data_root is None:
        raise FileNotFoundError("PlantDoc-Dataset test/train folder not found")

    logger.info(f"Building plant embed index from {data_root} (first run, ~1–2 min)...")
    labels = []
    vectors = []
    for class_dir in sorted(p for p in data_root.iterdir() if p.is_dir()):
        images = sorted(
            list(class_dir.glob("*.jpg"))
            + list(class_dir.glob("*.jpeg"))
            + list(class_dir.glob("*.png"))
            + list(class_dir.glob("*.JPG"))
        )[:max_per_class]
        embs = []
        for img_path in images:
            v = _embed_path(img_path)
            if v is not None:
                embs.append(v)
        if not embs:
            continue
        mean = np.mean(embs, axis=0)
        mean = mean / (np.linalg.norm(mean) + 1e-8)
        labels.append(class_dir.name)
        vectors.append(mean.astype("float32"))
        logger.info(f"  indexed {class_dir.name} ({len(embs)} images)")

    vectors = np.stack(vectors, axis=0)
    np.savez(CACHE_PATH, labels=np.array(labels, dtype=object), vectors=vectors)
    _index = {lab: vectors[i] for i, lab in enumerate(labels)}
    logger.info(f"Saved plant embed index -> {CACHE_PATH}")
    return _index


def _looks_like_soil_not_plant(image_path: str) -> bool:
    img = cv2.imread(image_path)
    if img is None:
        return False
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype("float32")
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green_dom = (g > r + 15) & (g > b + 15) & (g > 60)
    green_ratio = float(np.mean(green_dom))
    earth = (r > 40) & (r > b) & (np.abs(r - g) < 80) & (g > 20)
    earth_ratio = float(np.mean(earth))
    return earth_ratio > 0.4 and green_ratio < 0.12


def _predict_embed(image_path: str) -> dict:
    from treatments import treatment_for

    if _looks_like_soil_not_plant(image_path):
        return {
            "error": "This looks like soil / ground, not a plant leaf. Please upload a plant leaf image only.",
            "status": "invalid_image",
            "uncertain": True,
        }

    index = _build_or_load_index()
    q = _embed_path(Path(image_path))
    if q is None:
        return {"error": f"Could not load image -> {image_path}"}

    scores = []
    for name, proto in index.items():
        scores.append((name, float(np.dot(q, proto))))
    scores.sort(key=lambda x: -x[1])

    def to_conf(sim):
        return round(max(0.0, min(1.0, (sim + 1) / 2)), 4)

    top = [{"class": n, "confidence": to_conf(s)} for n, s in scores[:3]]
    best_name, best_sim = scores[0]
    margin = best_sim - (scores[1][1] if len(scores) > 1 else 0)
    conf = to_conf(best_sim)
    if margin > 0.05:
        conf = round(min(0.99, conf + 0.15), 4)

    # Raw cosine too low => not a leaf-like photo
    if best_sim < 0.42:
        return {
            "error": "Could not detect a plant leaf in this image. Please upload a clear close-up of a leaf only.",
            "status": "invalid_image",
            "uncertain": True,
            "confidence": conf,
        }

    uncertain = margin < 0.03 or conf < 0.55
    status = "HEALTHY" if best_name in HEALTHY else "DISEASED"
    if uncertain:
        status = "UNCERTAIN"

    treatment = treatment_for(best_name)

    return {
        "class": best_name,
        "confidence": conf,
        "status": status,
        "uncertain": uncertain,
        "top_predictions": top,
        "treatment": treatment,
        "engine": "imagenet-embed-match",
        "message": (
            "Model is unsure — try a sharper close-up of a single leaf."
            if uncertain
            else f"Closest match: {best_name}"
        ),
    }


def _predict_torch_worker(image_path: str):
    if not WORKER_PY.exists() or not WORKER.exists():
        return None
    try:
        proc = subprocess.run(
            [str(WORKER_PY), str(WORKER), image_path],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(ROOT),
            env={**os.environ, "KERAS_BACKEND": "torch"},
        )
        if proc.returncode != 0:
            logger.warning(f"Torch worker failed: {proc.stderr[-500:]}")
            return None
        line = proc.stdout.strip().splitlines()[-1]
        data = json.loads(line)
        if data.get("error"):
            return None
        return data
    except Exception as e:
        logger.warning(f"Torch worker error: {e}")
        return None


def predict_disease(image_path):
    try:
        image_path = os.path.normpath(image_path)
        if not os.path.exists(image_path):
            return {"error": f"Image file not found -> {image_path}"}

        # Prefer embedding matcher (works reliably with PlantDoc-style photos)
        result = _predict_embed(image_path)

        # If uncertain, try original Keras3 model and take it only if more confident
        if result.get("uncertain"):
            torch_res = _predict_torch_worker(image_path)
            if torch_res and not torch_res.get("uncertain") and torch_res.get("confidence", 0) > result.get("confidence", 0):
                return torch_res

        return result
    except Exception as e:
        logger.error(f"Plant disease prediction error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    print(json.dumps(predict_disease(path), indent=2))
