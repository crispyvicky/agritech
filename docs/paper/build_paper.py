"""Build the AgriSync IEEE paper (.docx) using the reference paper as a formatting template.

Every paragraph, the table and the figure are cloned from prototype elements of the
reference document, so fonts, sizes, spacing, margins and the two-column layout match it.

Usage:
    python docs/paper/build_paper.py
"""
import copy
import json
from pathlib import Path

import docx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from docx.oxml.ns import qn
from PIL import Image

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "ieee_reference_template.docx"
METRICS = HERE / "metrics.json"
FIG_PATH = HERE / "fig1_architecture.png"
OUT = HERE.parent / "AgriSync_IEEE_Paper.docx"

EMU_PER_INCH = 914400
FIG_WIDTH_IN = 3.14


# --------------------------------------------------------------------------- figure
def draw_architecture(path):
    plt.rcParams["font.family"] = "Times New Roman"
    fig, ax = plt.subplots(figsize=(4.4, 5.2), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")

    def box(x, y, w, h, text, fs=7.5, bold=False, fill="white", lw=0.8, style="round,pad=0.02,rounding_size=0.15"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fill, ec="black", lw=lw))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else "normal", wrap=True)

    def tier(y, h, title):
        ax.add_patch(FancyBboxPatch((0.2, y), 9.6, h, boxstyle="round,pad=0.02,rounding_size=0.25",
                                    fc="#f2f2f2", ec="black", lw=1.1))
        ax.text(5, y + h - 0.32, title, ha="center", va="center", fontsize=8.5, fontweight="bold")

    def arrow(y_top, y_bot, label):
        ax.add_patch(FancyArrowPatch((5, y_top), (5, y_bot), arrowstyle="<|-|>", mutation_scale=9,
                                     lw=1.0, color="black"))
        ax.text(5.25, (y_top + y_bot) / 2, label, ha="left", va="center", fontsize=6.5, style="italic")

    tier(9.1, 2.7, "Presentation Layer (React + Tailwind CSS)")
    for i, t in enumerate(["Leaf Disease\nDetection Page", "Soil Detection\nPage", "Crop Advisor\nPage"]):
        box(0.55 + i * 3.05, 9.35, 2.8, 1.45, t)

    arrow(9.05, 8.25, "HTTPS / JSON requests")

    tier(4.95, 3.25, "API and Validation Layer (FastAPI)")
    for i, t in enumerate(["POST /predict", "POST /predict-soil", "POST /predict-crop"]):
        box(0.55 + i * 3.05, 6.55, 2.8, 0.95, t)
    box(0.55, 5.2, 8.9, 1.05,
        "Input validation: leaf/soil colour checks,\ncosine-similarity threshold, numeric range checks", fs=7)

    arrow(4.9, 4.1, "Lazy model loading")

    tier(0.2, 3.85, "Model and Knowledge Layer")
    box(0.55, 2.0, 4.3, 1.2, "EfficientNetB0 embedder\n(ImageNet weights)")
    box(5.15, 2.0, 4.3, 1.2, "Prototype indexes\n(27 leaf, 4 soil classes)")
    box(0.55, 0.45, 4.3, 1.2, "Random Forest classifier\n(22 crops, 7 features)")
    box(5.15, 0.45, 4.3, 1.2, "Treatment and soil-care\nknowledge base")

    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------- docx helpers
def _clear_runs(p):
    for child in list(p):
        if child.tag != qn("w:pPr"):
            p.remove(child)


def _first_rpr(proto):
    for r in proto.iter(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is not None and r.find(qn("w:t")) is not None:
            return rpr
    return None


def _set_flag(rpr, tag, on):
    el = rpr.find(qn(tag))
    if on and el is None:
        new = rpr.makeelement(qn(tag), {})
        anchor = rpr.find(qn("w:rFonts"))
        if anchor is not None:
            anchor.addnext(new)
        else:
            rpr.insert(0, new)
    elif not on and el is not None:
        rpr.remove(el)


def make_para(proto, segments, rpr_from=None):
    """Clone `proto` and fill it with `segments` = [(text, bold, italic), ...] or a plain string.

    bold/italic of None keeps the prototype run's own setting.
    """
    if isinstance(segments, str):
        segments = [(segments, None, None)]
    p = copy.deepcopy(proto)
    base = copy.deepcopy(_first_rpr(rpr_from if rpr_from is not None else proto))
    _clear_runs(p)
    for text, bold, italic in segments:
        r = p.makeelement(qn("w:r"), {})
        if base is not None:
            rpr = copy.deepcopy(base)
            if bold is not None:
                _set_flag(rpr, "w:b", bold)
            if italic is not None:
                _set_flag(rpr, "w:i", italic)
            r.append(rpr)
        t = r.makeelement(qn("w:t"), {})
        t.text = text
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r.append(t)
        p.append(r)
    return p


def make_figure_para(doc, proto_with_drawing, png_path):
    p = copy.deepcopy(proto_with_drawing)
    for r in list(p.iter(qn("w:r"))):
        if r.find(qn("w:drawing")) is None:
            r.getparent().remove(r)
    ppr = p.find(qn("w:pPr"))
    ind = ppr.find(qn("w:ind"))
    if ind is not None:
        ppr.remove(ind)
    ppr.find(qn("w:jc")).set(qn("w:val"), "center")

    blip = next(p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))
    rid = blip.get(qn("r:embed"))
    doc.part.related_parts[rid]._blob = png_path.read_bytes()

    w_px, h_px = Image.open(png_path).size
    cx = int(FIG_WIDTH_IN * EMU_PER_INCH)
    cy = int(cx * h_px / w_px)
    for tag in ("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent",
                "{http://schemas.openxmlformats.org/drawingml/2006/main}ext"):
        for el in p.iter(tag):
            el.set("cx", str(cx))
            el.set("cy", str(cy))
    for el in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr"):
        el.set("descr", "AgriSync three-tier system architecture")
    return p


def make_table(proto_tbl, rows):
    tbl = copy.deepcopy(proto_tbl)
    for tr, values in zip(tbl.iter(qn("w:tr")), rows):
        for tc, value in zip(tr.iter(qn("w:tc")), values):
            p = tc.find(qn("w:p"))
            for extra in tc.findall(qn("w:p"))[1:]:
                tc.remove(extra)
            new_p = make_para(p, value)
            tc.replace(p, new_p)
    return tbl


# --------------------------------------------------------------------------- content
def pct(x, digits=1):
    return f"{x * 100:.{digits}f}%"


def build_content(m):
    leaf, soil, crop = m["leaf_disease"], m["soil_type"], m["crop_recommendation"]
    crop_metrics = json.loads((HERE.parents[1] / "backend" / "models" / "crop_recommender_metrics.json").read_text())
    top_feats = list(crop_metrics["feature_importance"])[:3]
    feat_names = {"N": "nitrogen", "P": "phosphorus", "K": "potassium", "ph": "pH",
                  "temperature": "temperature", "humidity": "humidity", "rainfall": "rainfall"}
    top_feats = [feat_names[f] for f in top_feats]
    max_latency = max(leaf["avg_latency_ms"], soil["avg_latency_ms"], crop["avg_latency_ms"])
    latency_bound = int((max_latency // 50 + 1) * 50)

    title = ("AgriSync: An Integrated AI Framework for Leaf Disease Detection, "
             "Soil Classification, and Crop Recommendation")

    abstract = (
        "Farmers routinely lose a significant share of their harvest to undiagnosed plant diseases, poorly "
        "understood soils, and crop choices driven by habit rather than field conditions; however, existing "
        "digital agriculture tools usually address only one of these decisions in isolation. This paper "
        "introduces AgriSync, a web-based decision-support framework that unifies three agricultural prediction "
        "services: leaf disease detection, soil type classification, and crop recommendation. The leaf and soil modules "
        "use a training-free approach in which ImageNet-pretrained EfficientNetB0 embeddings are matched against "
        "class prototypes by cosine similarity, while the crop recommendation module uses a Random Forest "
        "trained on soil nutrients (N, P, K), pH, temperature, humidity, and rainfall. The system is built on a "
        "FastAPI backend and a React frontend. Experimental evaluation on held-out data shows "
        f"{pct(crop['top1_accuracy'], 2)} crop recommendation accuracy, {pct(soil['top3_accuracy'])} top-3 soil "
        f"accuracy, and inference latency below {latency_bound} ms on an ordinary CPU."
    )
    keywords = ("Precision Agriculture, Plant Disease Detection, Soil Classification, Crop Recommendation, "
                "EfficientNet, Random Forest, FastAPI.")

    intro = [
        "Agriculture remains the primary source of livelihood for a large share of the population in developing "
        "economies, and India alone loses an estimated 35 percent of its annual crop yield to plant diseases [2]. "
        "Farmers must routinely make three interlinked decisions: identifying whether a crop is diseased, "
        "understanding the soil they are working with, and choosing which crop to sow in the coming season. "
        "Advances in deep learning and machine learning have shown strong potential for supporting each of these "
        "decisions from photographs and simple field measurements [6], [7].",

        "In practice, however, these decisions are still made largely through intuition, inherited practice, or "
        "occasional visits from extension officers. Laboratory soil testing and expert plant pathology are "
        "expensive and slow to reach rural areas. Furthermore, a single misjudged decision, such as sowing a "
        "water-intensive crop in a low-rainfall season, can cause losses that persist across an entire year.",

        "Prior research has produced accurate models for individual tasks, notably convolutional neural networks "
        "for leaf disease classification [1] and machine-learning classifiers for crop selection [8]. However, "
        "most of these solutions remain standalone research prototypes trained on controlled laboratory images "
        "and are rarely delivered to farmers as a usable application. Models trained on laboratory images also "
        "degrade sharply on real field photographs with cluttered backgrounds [2].",

        "This paper presents AgriSync, an open-source, web-based agricultural decision-support platform that "
        "combines image-based and data-driven predictions behind a single, simple interface. The primary "
        "contributions of this work are fourfold:",

        "(1) Unified Agricultural Prediction Platform: Integrating leaf disease detection, soil type "
        "classification, and crop recommendation into one FastAPI service consumed by a responsive React dashboard.",

        "(2) Training-Free Image Recognition: Using ImageNet-pretrained EfficientNetB0 embeddings with "
        "cosine-similarity prototype matching, so that new disease or soil classes can be added by supplying a few "
        "reference images instead of retraining a network.",

        "(3) Data-Driven Crop Recommendation: Introducing a Random Forest classifier that recommends the most "
        "suitable of 22 crops from soil nutrients, pH, and local climate, returning the top three options with "
        "confidence scores.",

        "(4) Transparent Empirical Evaluation: Measuring top-1 accuracy, top-3 accuracy, macro F1-score, and "
        "inference latency for all three modules on data that was not used to build or train the models.",
    ]

    related_intro = ("AgriSync builds on two established lines of agricultural artificial intelligence research: "
                     "image-based crop health assessment and data-driven soil and crop management.")
    related_a = (
        "Mohanty et al. [1] trained deep convolutional networks on 54,306 laboratory leaf images and reached 99.35 "
        "percent accuracy. However, Singh et al. [2] showed that such models generalize poorly to field photographs "
        "and released PlantDoc, a 27-class in-the-wild dataset on which a fine-tuned VGG16 reached only 29.73 "
        "percent accuracy on uncropped images. Kamilaris and Prenafeta-Boldu [6] likewise identified realistic "
        "training data as a recurring limitation."
    )
    related_b = (
        "Liakos et al. [7] reviewed machine-learning applications in crop, water, and soil management and "
        "highlighted ensemble methods for tabular agronomic data. Doshi et al. [8] proposed AgroConsultant, which "
        "recommends crops from location, season, soil, temperature, and rainfall, reporting 90.43 percent accuracy "
        "with a Random Forest [5]. However, most existing systems treat soil identification and crop selection as "
        "separate tools and do not combine them with visual disease diagnosis in a single farmer-facing application."
    )

    arch_intro = ("AgriSync is engineered as a modular client-server application featuring a responsive web "
                  "interface, a lightweight REST backend, and a local model store that requires no external "
                  "cloud services.")
    arch_a = (
        "The system architecture is structured into three distinct operational tiers to ensure separation of "
        "concerns and fast response: Presentation Layer: The client-side tier is a React and Tailwind CSS "
        "single-page application with three tool pages. Farmers upload a leaf photograph, upload a soil "
        "photograph, or enter seven field readings, and immediately view the prediction, its confidence, and "
        "practical guidance. API and Validation Layer: A FastAPI backend exposes the /predict, /predict-soil, and "
        "/predict-crop endpoints. It stores uploads temporarily, validates inputs (colour checks for images and "
        "range checks for field readings), and routes each request to the appropriate predictor. Model and Knowledge Layer: This tier holds the EfficientNetB0 feature "
        "extractor, precomputed class-prototype indexes for 27 leaf classes and 4 soil classes, the trained Random "
        "Forest model, and curated treatment and soil-care knowledge, all loaded lazily on first use."
    )
    fig_caption = ("Fig. 1. High-level three-tier system architecture of AgriSync showing the Presentation, "
                   "FastAPI API and Validation, and Model and Knowledge layers.")
    arch_b = (
        "The prediction workflow distributes responsibilities across three independent modules, each of which can "
        "be invoked separately from the dashboard: Leaf Disease Detection Module: An uploaded leaf image is resized "
        "to 224 x 224 pixels and passed through EfficientNetB0 [3], pretrained on ImageNet [4], to produce an "
        "L2-normalised 1,280-dimensional embedding. The embedding is compared by cosine similarity with the mean "
        "prototype of each of the 27 PlantDoc classes, and the three closest matches are returned with a healthy or "
        "diseased status and treatment advice. Soil Classification Module: The same embedder is applied to soil "
        "photographs and matched against prototypes for Alluvial, Black, Clay, and Red soil. The response includes "
        "soil notes, care tips, and crops typically suited to that soil. Crop Recommendation Module: The farmer "
        "enters nitrogen, phosphorus, and potassium levels, soil pH, temperature, humidity, and rainfall, and a "
        "Random Forest returns the most suitable crop together with two alternatives and their class probabilities. "
        "Inputs with very low similarity or out-of-range values are rejected with a clear message rather than a "
        "misleading prediction."
    )

    impl_intro = ("The implementation emphasizes simplicity, low hardware requirements, and reproducibility, so "
                  "that the complete platform runs on an ordinary laptop CPU.")
    impl_a = (
        "The backend uses Python's FastAPI framework with Pydantic request validation and lazy model loading, so "
        "TensorFlow is loaded only when an image endpoint is first called. Prototype indexes are stored as compact "
        "NumPy archives and the crop model is serialised with joblib, giving a total model footprint below 23 MB "
        "including the shared EfficientNetB0 weights."
    )
    impl_b = (
        "Because the image modules are training-free, a new disease or soil class only requires a few labelled "
        "reference images; prototypes are averaged from eight leaf images and ten soil images per class. The crop "
        f"model was trained on a public dataset of {crop_metrics['samples']:,} samples covering "
        f"{crop_metrics['classes']} crops with seven numeric features, using a stratified 80/20 split and 200 trees. "
        f"Training takes under one second on a CPU, with {top_feats[0]}, {top_feats[1]}, and {top_feats[2]} as the "
        "most important features."
    )

    eval_intro = ("To evaluate the accuracy, responsiveness, and practicality of AgriSync, each module was tested "
                  "on data that was not used to build its prototypes or train its model, using a consumer laptop "
                  "CPU without GPU acceleration.")
    eval_a = (
        "The evaluation framework measures three primary performance dimensions: (1) Top-1 and Top-3 Accuracy, "
        "the percentage of samples whose true class is the first prediction or among the first three; (2) Macro "
        "F1-Score, the unweighted mean F1-score across classes, which accounts for class imbalance; and (3) "
        "Inference Latency, the average time of a single end-to-end prediction including image decoding and "
        f"validation. Leaf disease detection was evaluated on {leaf['images']:,} held-out PlantDoc images, soil "
        f"classification on {soil['images']:,} held-out soil images, and crop recommendation on a "
        f"{crop['images']}-sample stratified test split."
    )
    table_rows = [
        ["Prediction Module", "Top-1 / Top-3 Accuracy", "Avg. Inference Latency"],
        [f"Leaf Disease Detection ({leaf['classes']} classes)",
         f"{pct(leaf['top1_accuracy'])} / {pct(leaf['top3_accuracy'])}", f"{leaf['avg_latency_ms']:.0f} ms"],
        [f"Soil Classification ({soil['classes']} classes)",
         f"{pct(soil['top1_accuracy'])} / {pct(soil['top3_accuracy'])}", f"{soil['avg_latency_ms']:.0f} ms"],
        [f"Crop Recommendation ({crop['classes']} crops)",
         f"{pct(crop['top1_accuracy'])} / {pct(crop['top3_accuracy'])}", f"{crop['avg_latency_ms']:.0f} ms"],
    ]
    table_caption = "TABLE I. QUANTITATIVE PERFORMANCE METRICS OF THE THREE AGRISYNC PREDICTION MODULES."
    eval_b = (
        f"Experimental results show that the crop recommendation module achieves {pct(crop['top1_accuracy'], 2)} "
        f"top-1 accuracy with a macro F1-score of {crop['macro_f1']:.3f}. The soil module reaches "
        f"{pct(soil['top1_accuracy'])} top-1 and {pct(soil['top3_accuracy'])} top-3 accuracy, while the leaf "
        f"module achieves {pct(leaf['top1_accuracy'])} top-1 and {pct(leaf['top3_accuracy'])} top-3 accuracy "
        "across 27 field-condition classes, comparable to the 29.73 percent of a fine-tuned VGG16 on uncropped "
        f"PlantDoc images [2] despite requiring no training. All modules respond in under {latency_bound} ms on a "
        "CPU, and the image results are best presented to farmers as ranked suggestions."
    )

    conclusion = (
        "This paper introduced AgriSync, an integrated agricultural decision-support framework that brings leaf "
        "disease detection, soil classification, and crop recommendation together in a single web application. By "
        "combining training-free EfficientNetB0 prototype matching with a Random Forest crop recommender behind a "
        "lightweight FastAPI backend, the system delivers fast and easily extensible predictions on ordinary "
        "hardware. The crop recommender proved highly accurate, while the image modules provide useful ranked "
        "suggestions. Future work will fine-tune the image modules on larger field datasets, add leaf localisation, "
        "and connect live weather data to the crop recommender."
    )
    acknowledgment = (
        "The authors gratefully acknowledge the creators of the PlantDoc and Crop Recommendation datasets, and the "
        "open-source communities behind TensorFlow, scikit-learn, FastAPI, and React, whose tools and data made "
        "this research platform possible."
    )
    references = [
        '[1] S. P. Mohanty, D. P. Hughes, and M. Salathe, "Using deep learning for image-based plant disease '
        'detection," Front. Plant Sci., vol. 7, Art. no. 1419, Sept. 2016.',
        '[2] D. Singh, N. Jain, P. Jain, P. Kayal, S. Kumawat, and N. Batra, "PlantDoc: A dataset for visual plant '
        'disease detection," in Proc. 7th ACM IKDD CoDS and 25th COMAD, Hyderabad, India, 2020, pp. 249-253.',
        '[3] M. Tan and Q. Le, "EfficientNet: Rethinking model scaling for convolutional neural networks," in Proc. '
        '36th Int. Conf. Mach. Learn. (ICML), PMLR vol. 97, 2019, pp. 6105-6114.',
        '[4] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei, "ImageNet: A large-scale hierarchical '
        'image database," in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), 2009, pp. 248-255.',
        '[5] L. Breiman, "Random forests," Mach. Learn., vol. 45, no. 1, pp. 5-32, Oct. 2001.',
        '[6] A. Kamilaris and F. X. Prenafeta-Boldu, "Deep learning in agriculture: A survey," Comput. Electron. '
        'Agric., vol. 147, pp. 70-90, Apr. 2018.',
        '[7] K. G. Liakos, P. Busato, D. Moshou, S. Pearson, and D. Bochtis, "Machine learning in agriculture: A '
        'review," Sensors, vol. 18, no. 8, Art. no. 2674, Aug. 2018.',
        '[8] Z. Doshi, S. Nadkarni, R. Agrawal, and N. Shah, "AgroConsultant: Intelligent crop recommendation system '
        'using machine learning algorithms," in Proc. 4th Int. Conf. Comput. Commun. Control Autom. (ICCUBEA), '
        'Pune, India, 2018.',
    ]

    return locals()


# --------------------------------------------------------------------------- assembly
def main():
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    c = build_content(metrics)
    draw_architecture(FIG_PATH)

    doc = docx.Document(str(TEMPLATE))
    body = doc.element.body
    els = list(body)
    P = {
        "title": els[0], "authors": els[1], "aff1": els[2], "aff2": els[3],
        "abstract": els[4], "keywords": els[5], "col_break": els[6],
        "heading": els[7], "body": els[8], "sub": els[18],
        "figure": els[25], "caption": els[26], "table": els[39], "tcaption": els[40],
        "ref": els[48],
    }
    final_sectpr = els[-1]

    out = [
        make_para(P["title"], c["title"]),
        copy.deepcopy(P["authors"]),
        copy.deepcopy(P["aff1"]),
        copy.deepcopy(P["aff2"]),
        make_para(P["abstract"], [("Abstract- ", True, None), (c["abstract"], False, None)]),
        make_para(P["keywords"], [("Keywords\u2014 ", True, True), (c["keywords"], False, True)]),
        copy.deepcopy(P["col_break"]),
    ]

    def heading(t):
        out.append(make_para(P["heading"], t))

    def sub(t):
        out.append(make_para(P["sub"], t))

    def para(t):
        out.append(make_para(P["body"], t))

    heading("I. INTRODUCTION")
    for t in c["intro"]:
        para(t)

    heading("II. RELATED WORK")
    para(c["related_intro"])
    sub("A. Deep Learning for Plant Disease Detection")
    para(c["related_a"])
    sub("B. Soil Classification and Crop Recommendation Systems")
    para(c["related_b"])

    heading("III. SYSTEM ARCHITECTURE AND PREDICTION WORKFLOW")
    para(c["arch_intro"])
    sub("A. High-Level System Architecture")
    para(c["arch_a"])
    out.append(make_figure_para(doc, P["figure"], FIG_PATH))
    out.append(make_para(P["caption"], c["fig_caption"]))
    sub("B. Prediction Modules and Workflow")
    para(c["arch_b"])

    heading("IV. IMPLEMENTATION DETAILS")
    para(c["impl_intro"])
    sub("A. Backend Design and Model Storage")
    para(c["impl_a"])
    sub("B. Feature Extraction and Model Training")
    para(c["impl_b"])

    heading("V. EXPERIMENTAL EVALUATION")
    para(c["eval_intro"])
    sub("A. Evaluation Metrics and Methodology")
    para(c["eval_a"])
    out.append(make_table(P["table"], c["table_rows"]))
    out.append(make_para(P["tcaption"], c["table_caption"]))
    sub("B. Empirical Results and Discussion")
    para(c["eval_b"])

    heading("VI. CONCLUSION")
    para(c["conclusion"])
    heading("ACKNOWLEDGMENT")
    para(c["acknowledgment"])
    heading("REFERENCES")
    for ref in c["references"]:
        out.append(make_para(P["ref"], ref))

    for el in els:
        body.remove(el)
    for el in out:
        body.append(el)
    body.append(final_sectpr)

    doc.core_properties.title = c["title"]
    doc.core_properties.subject = "IEEE conference paper"
    doc.core_properties.keywords = c["keywords"]
    doc.save(str(OUT))
    print(f"Saved {OUT}")
    print(f"Saved {FIG_PATH}")


if __name__ == "__main__":
    main()
