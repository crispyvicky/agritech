"""Measure accuracy and latency of the three AgriSync prediction modules for the paper.

Leaf and soil are scored on images that were NOT used to build the shipped prototype
indexes (PlantDoc train split, Soil Train split). Crop uses the stratified 20% test split.

Usage:
    python docs/paper/evaluate_modules.py --data-root <folder containing PlantDoc-Dataset and Soil>
"""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND / "scripts"))

IMG_EXT = {".jpg", ".jpeg", ".png"}


def load_index(npz_path):
    data = np.load(npz_path, allow_pickle=True)
    return [str(l) for l in data["labels"]], data["vectors"].astype("float32")


def list_images(split_dir, labels):
    items = []
    for class_dir in sorted(p for p in split_dir.iterdir() if p.is_dir()):
        if class_dir.name not in labels:
            continue
        for p in sorted(class_dir.iterdir()):
            if p.suffix.lower() in IMG_EXT:
                items.append((p, class_dir.name))
    return items


def embed_batch(model, paths):
    from tensorflow.keras.applications.efficientnet import preprocess_input

    batch, ok = [], []
    for i, p in enumerate(paths):
        img = cv2.imread(str(p))
        if img is None:
            continue
        img = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (224, 224)).astype("float32")
        batch.append(img)
        ok.append(i)
    if not batch:
        return np.zeros((0, 1280), "float32"), ok
    v = model.predict(preprocess_input(np.stack(batch)), verbose=0)
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-8), ok


def macro_f1(y_true, y_pred, labels):
    f1s = []
    for lab in labels:
        tp = sum(t == lab and p == lab for t, p in zip(y_true, y_pred))
        fp = sum(t != lab and p == lab for t, p in zip(y_true, y_pred))
        fn = sum(t == lab and p != lab for t, p in zip(y_true, y_pred))
        if tp + fp + fn == 0:
            continue
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return float(np.mean(f1s)) if f1s else 0.0


def eval_image_module(name, model, npz_path, split_dir, single_fn, batch_size=32):
    labels, protos = load_index(npz_path)
    items = list_images(split_dir, set(labels))
    y_true, y_pred, top3_hits = [], [], 0
    for start in range(0, len(items), batch_size):
        chunk = items[start:start + batch_size]
        vecs, ok = embed_batch(model, [p for p, _ in chunk])
        sims = vecs @ protos.T
        for row, i in zip(sims, ok):
            truth = chunk[i][1]
            order = np.argsort(-row)
            y_true.append(truth)
            y_pred.append(labels[order[0]])
            top3_hits += truth in {labels[j] for j in order[:3]}
        print(f"  {name}: {min(start + batch_size, len(items))}/{len(items)}", end="\r")
    print()

    sample = [p for p, _ in items[:: max(1, len(items) // 30)]][:30]
    single_fn(sample[0])
    t0 = time.perf_counter()
    for p in sample:
        single_fn(p)
    latency_ms = (time.perf_counter() - t0) / len(sample) * 1000

    n = len(y_true)
    return {
        "eval_split": str(split_dir.relative_to(split_dir.parents[1])),
        "classes": len(labels),
        "images": n,
        "top1_accuracy": round(sum(t == p for t, p in zip(y_true, y_pred)) / n, 4),
        "top3_accuracy": round(top3_hits / n, 4),
        "macro_f1": round(macro_f1(y_true, y_pred, labels), 4),
        "avg_latency_ms": round(latency_ms, 1),
    }


def eval_crop():
    import pandas as pd
    from sklearn.model_selection import train_test_split

    from predict_crop import recommend_crop, _load

    bundle = _load()
    model, feats = bundle["model"], bundle["features"]
    df = pd.read_csv(BACKEND / "data" / "crop_recommendation.csv")
    _, X_test, _, y_test = train_test_split(
        df[feats], df["label"], test_size=0.2, stratify=df["label"], random_state=42
    )
    proba = model.predict_proba(X_test)
    order = np.argsort(-proba, axis=1)
    classes = model.classes_
    y_pred = classes[order[:, 0]]
    top3 = np.mean([t in set(classes[o[:3]]) for t, o in zip(y_test, order)])

    rows = X_test.to_dict("records")
    recommend_crop(rows[0])
    t0 = time.perf_counter()
    for r in rows[:100]:
        recommend_crop(r)
    latency_ms = (time.perf_counter() - t0) / 100 * 1000

    return {
        "eval_split": "stratified 20% test split",
        "classes": int(len(classes)),
        "images": int(len(y_test)),
        "top1_accuracy": round(float(np.mean(y_pred == y_test.values)), 4),
        "top3_accuracy": round(float(top3), 4),
        "macro_f1": round(macro_f1(list(y_test), list(y_pred), list(classes)), 4),
        "avg_latency_ms": round(latency_ms, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, default=BACKEND)
    ap.add_argument("--out", type=Path, default=Path(__file__).with_name("metrics.json"))
    args = ap.parse_args()

    import predict_plantdoc
    import predict_soil_embed

    model = predict_plantdoc._get_embed_model()
    predict_soil_embed._model = model

    results = {
        "leaf_disease": eval_image_module(
            "leaf",
            model,
            BACKEND / "models" / "plantdoc_embed_index.npz",
            args.data_root / "PlantDoc-Dataset" / "train",
            lambda p: predict_plantdoc._predict_embed(str(p)),
        ),
        "soil_type": eval_image_module(
            "soil",
            model,
            BACKEND / "models" / "soil_embed_index.npz",
            args.data_root / "Soil" / "Train",
            lambda p: predict_soil_embed.predict_soil_from_path(str(p)),
        ),
        "crop_recommendation": eval_crop(),
    }
    args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
