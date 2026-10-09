"""
AgriTech college project documentation PDF
— same chapter/subheading style as docs/backshot final.pdf
"""
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[1]
DOCS = Path(__file__).resolve().parent
OUT_DOCS = DOCS / "AgriTech final.pdf"
OUT_ROOT = ROOT / "AgriTech_Project_Documentation.pdf"
DEMO = ROOT / "DEMO_TESTED_IMAGES"


def styles():
    base = getSampleStyleSheet()
    return {
        "chapter": ParagraphStyle(
            "Chapter", parent=base["Heading1"], fontName="Times-Bold",
            fontSize=14, leading=18, alignment=TA_CENTER, spaceBefore=6, spaceAfter=4,
        ),
        "chapter_title": ParagraphStyle(
            "ChapterTitle", parent=base["Heading1"], fontName="Times-Bold",
            fontSize=13, leading=17, alignment=TA_CENTER, spaceBefore=2, spaceAfter=14,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Times-Bold",
            fontSize=12, leading=16, alignment=TA_LEFT, spaceBefore=12, spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="Times-Bold",
            fontSize=11, leading=14, spaceBefore=8, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=16, alignment=TA_JUSTIFY, spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=15, leftIndent=18, spaceAfter=3,
        ),
        "num": ParagraphStyle(
            "Num", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=15, leftIndent=18, spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "Code", fontName="Courier", fontSize=8.5, leading=11,
            leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=10,
            backColor=colors.HexColor("#f5f5f5"),
        ),
        "code_title": ParagraphStyle(
            "CodeTitle", fontName="Times-Bold", fontSize=10.5,
            leading=13, spaceBefore=8, spaceAfter=4,
        ),
        "fig": ParagraphStyle(
            "Fig", fontName="Times-Italic", fontSize=10, leading=13,
            alignment=TA_CENTER, spaceBefore=4, spaceAfter=12,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle", fontName="Times-Bold", fontSize=18,
            leading=24, alignment=TA_CENTER, spaceAfter=10,
        ),
        "cover_sub": ParagraphStyle(
            "CoverSub", fontName="Times-Roman", fontSize=12,
            leading=16, alignment=TA_CENTER, spaceAfter=6,
        ),
        "ref": ParagraphStyle(
            "Ref", fontName="Times-Roman", fontSize=10.5, leading=14,
            leftIndent=18, firstLineIndent=-18, spaceAfter=5,
        ),
    }


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    canvas.drawCentredString(A4[0] / 2, A4[1] - 0.55 * inch, str(doc.page))
    canvas.restoreState()


def chapter_header(story, st, number, title):
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"CHAPTER – {number}", st["chapter"]))
    story.append(Paragraph(title, st["chapter_title"]))


def table_style():
    return TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


def maybe_image(path: Path, width=4.6 * inch, caption="", st=None):
    st = st or styles()
    if not path.exists():
        return [Paragraph(f"[Image missing: {path.name}]", st["fig"])]
    img = Image(str(path), width=width, height=width * 0.75, kind="proportional")
    img.hAlign = "CENTER"
    out = [Spacer(1, 8), img]
    if caption:
        out.append(Paragraph(caption, st["fig"]))
    out.append(Spacer(1, 6))
    return out


def build():
    st = styles()
    doc = SimpleDocTemplate(
        str(OUT_DOCS), pagesize=A4,
        leftMargin=1.0 * inch, rightMargin=1.0 * inch,
        topMargin=0.85 * inch, bottomMargin=0.75 * inch,
        title="AgriTech — Project Documentation", author="AgriTech",
    )
    story = []

    # ========== COVER ==========
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("AGRITECH", st["cover_title"]))
    story.append(Paragraph(
        "AI-Powered Plant Disease Detection &amp; Soil Classification System",
        st["cover_sub"],
    ))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Project Documentation", st["cover_sub"]))
    story.append(Paragraph("(College Project Report)", st["cover_sub"]))
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph(
        "A web-based agricultural assistance system that uses deep-learning image embeddings "
        "to detect plant leaf diseases and classify soil types, and then provides treatment "
        "techniques and crop recommendations for practical farming decisions.",
        st["body"],
    ))
    story.append(Spacer(1, 0.9 * inch))
    story.append(Paragraph(
        "Frontend: React.js &nbsp;&nbsp;|&nbsp;&nbsp; Backend: FastAPI &nbsp;&nbsp;|&nbsp;&nbsp; AI: TensorFlow / Keras / EfficientNetB0",
        st["cover_sub"],
    ))
    story.append(Paragraph(
        "Core Modules: Plant Disease Detection · Soil Detection",
        st["cover_sub"],
    ))
    story.append(Paragraph(
        "Repository: https://github.com/crispyvicky/agritech.git",
        st["cover_sub"],
    ))
    story.append(PageBreak())

    # ========== ABSTRACT ==========
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph("ABSTRACT", st["chapter_title"]))
    story.append(Paragraph(
        "Plant disease identification and soil classification are important tasks in agriculture. "
        "Manual inspection is time-consuming and depends on expert knowledge. This project presents "
        "AgriTech, a web-based AI system that analyzes uploaded photographs of plant leaves and soil. "
        "The system uses a Convolutional Neural Network based feature extractor (EfficientNetB0 "
        "pretrained on ImageNet) to convert each image into an embedding vector. Class labels are "
        "assigned by cosine-similarity matching against class prototypes built from PlantDoc-style "
        "leaf images and soil training images. The platform also provides treatment tips for diseased "
        "leaves and crop suitability recommendations for soil types. Unrelated images are rejected "
        "with clear user guidance. The application is implemented with React.js and FastAPI and is "
        "suitable for college demonstration using a curated DEMO_TESTED_IMAGES pack.",
        st["body"],
    ))
    story.append(Paragraph(
        "<b>Keywords:</b> Plant disease detection, Soil classification, EfficientNetB0, "
        "Cosine similarity, Transfer learning, FastAPI, React.js, Agricultural decision support.",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== CHAPTER 1 ==========
    chapter_header(story, st, "1", "INTRODUCTION")

    story.append(Paragraph("1.1 Introduction", st["h2"]))
    story.append(Paragraph(
        "Agriculture depends on timely decisions about crop health and soil suitability. "
        "Farmers, students, and agronomy learners often rely on manual visual inspection of "
        "leaves and soil, which is slow and may give inconsistent results. Early detection of "
        "leaf disease and correct identification of soil type can reduce crop loss, guide "
        "treatment choices, and support better crop planning for a given field.",
        st["body"],
    ))
    story.append(Paragraph(
        "With the increasing availability of smartphones and digital cameras, image-based "
        "decision support has become practical. However, raw photographs vary in lighting, "
        "angle, and background. A useful system must not only classify an image, but also "
        "explain what the user should do next—for example which treatment technique to apply "
        "for a diseased leaf, or which crops can grow well in a given soil type.",
        st["body"],
    ))
    story.append(Paragraph(
        "AgriTech is proposed as an intelligent web application that simplifies this process. "
        "The user uploads a clear photograph through a browser interface. The backend runs a "
        "Machine Learning vision pipeline based on EfficientNetB0 embeddings and nearest-class "
        "prototype matching. The system returns a prediction with confidence along with "
        "practical guidance. For plant leaves, it reports the disease (or healthy) class and a "
        "short treatment tip when disease is present. For soil images, it reports the soil type "
        "and suggests suitable crops with basic care tips.",
        st["body"],
    ))
    story.append(Paragraph(
        "The application is developed using React.js for the interactive frontend, FastAPI for "
        "REST APIs, and TensorFlow/Keras for deep feature extraction. The presentation build "
        "focuses on two working image tools: Plant Disease Detection and Soil Detection. "
        "Verified demo images are kept in a dedicated folder so live demos remain reliable.",
        st["body"],
    ))

    story.append(Paragraph("1.2 Problem Statement", st["h2"]))
    story.append(Paragraph(
        "Identifying plant diseases and soil types from photographs is difficult without "
        "domain expertise. Users often upload random photos, mixed backgrounds, or the wrong "
        "kind of image (for example a soil photo into a plant tool). A naive classifier may "
        "still force a class label with very low confidence, which confuses the user and "
        "reduces trust during evaluation or demonstration.",
        st["body"],
    ))
    story.append(Paragraph(
        "Traditional methods of maintaining crop notes or using general photo apps do not "
        "provide agricultural guidance such as treatment steps or crop suitability. Spreadsheet "
        "records also fail to connect a visual symptom on a leaf with an actionable recommendation. "
        "Therefore, there is a need for an intelligent and user-friendly system that can:",
        st["body"],
    ))
    for t in [
        "Accept a leaf or soil image through a simple web UI.",
        "Run a clear Machine Learning algorithm (deep embedding + similarity matching).",
        "Reject unrelated uploads with an explicit message (plant leaf only / soil only).",
        "Return treatment techniques for diseases and crop suggestions for soil types.",
        "Support a clean live demonstration with known-good sample images.",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))

    story.append(Paragraph(
        "The AgriTech system addresses these challenges by integrating modern web technologies "
        "with AI-driven image analysis into a centralized platform for agricultural image "
        "assistance.",
        st["body"],
    ))

    story.append(Paragraph("1.3 Objective of Project", st["h2"]))
    story.append(Paragraph(
        "The main objective of AgriTech is to develop an intelligent and user-friendly system "
        "that helps individuals analyze plant and soil images and make informed agricultural "
        "decisions. The key objectives of the proposed system are:",
        st["body"],
    ))
    for i, t in enumerate([
        "To detect plant leaf diseases from a single uploaded leaf image using deep learning embeddings.",
        "To classify common soil types (Alluvial, Black, Clay, Red) from a soil photograph.",
        "To clearly document and implement the Machine Learning algorithm used (EfficientNetB0 + cosine similarity matching).",
        "To reject unrelated images (soil uploaded to the plant tool, or leaf uploaded to the soil tool).",
        "To display treatment tips / techniques for detected diseases.",
        "To suggest suitable crops and care tips for each soil type (what can be grown).",
        "To provide a clean web interface suitable for college presentation and viva demonstration.",
        "To organize verified demo images in one folder for accurate live results.",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph("1.4 Scope of the Project", st["h2"]))
    story.append(Paragraph(
        "The scope of AgriTech covers the development of an image-based agricultural assistance "
        "platform. The system combines web application features with AI/ML techniques to provide "
        "personalized insights and decision support. The major areas covered by the project are:",
        st["body"],
    ))
    scope_items = [
        ("1. Plant Disease Detection",
         "Users upload a clear leaf photo. The system returns class name, confidence, "
         "HEALTHY / DISEASED / UNCERTAIN status, top alternate predictions, and a treatment tip."),
        ("2. Soil Classification",
         "Users upload a soil photo. The system returns soil type, confidence, notes, "
         "suitable crops, and care tips."),
        ("3. Input Validation / Wrong-Image Handling",
         "Wrong-type images are rejected with a clear “upload plant leaf only” or "
         "“upload soil only” message instead of a forced wrong label."),
        ("4. Web Application Layer",
         "React frontend communicates with FastAPI endpoints /predict and /predict-soil."),
        ("5. Machine Learning Pipeline",
         "EfficientNetB0 feature extraction, prototype index building, cosine similarity ranking."),
        ("6. Guidance Knowledge Base",
         "Disease treatments (treatments.py) and soil crop/care dictionaries."),
        ("7. Demo Assets",
         "Verified sample images under DEMO_TESTED_IMAGES for presentation."),
        ("8. Documentation",
         "College-style project report and a separate beginner setup/run/present guide."),
    ]
    for title, text in scope_items:
        story.append(Paragraph(title, st["h3"]))
        story.append(Paragraph(text, st["body"]))

    story.append(PageBreak())

    # ========== CHAPTER 2 ==========
    chapter_header(story, st, "2", "PROBLEM IDENTIFICATION")

    story.append(Paragraph("2.1 Problem Identification", st["h2"]))
    story.append(Paragraph(
        "Crop health monitoring and soil assessment are essential for agriculture, but manual "
        "inspection requires experience and time. Students and farmers may not always have "
        "access to an expert when a leaf shows spots or when soil type is unclear. Mobile photos "
        "vary in lighting, angle, and background, which makes automatic recognition harder.",
        st["body"],
    ))
    story.append(Paragraph(
        "Managing agricultural decisions has become increasingly dependent on visual information. "
        "Individuals often need to interpret leaf symptoms and soil appearance while deciding "
        "about spraying, irrigation, and crop choice. Basic photo viewers or notebooks mainly "
        "store images; they generally provide limited analysis and do not offer personalized "
        "recommendations based on the content of the image.",
        st["body"],
    ))
    story.append(Paragraph("The major problems identified are:", st["body"]))
    for t in [
        "Difficulty in recognizing leaf diseases from casual photographs.",
        "Confusion between healthy leaves and diseased leaves with similar colors.",
        "Difficulty in identifying soil type from a field photo.",
        "Misleading results when unrelated images (non-leaf / non-soil) are uploaded.",
        "Low-confidence predictions that are hard for beginners to interpret.",
        "Lack of immediate treatment or crop guidance after a prediction.",
        "Scattered test images that make demos unreliable if the wrong files are used.",
        "Need for a simple, documented demo path for presentations and evaluation.",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))

    story.append(Paragraph("2.2 Existing Problems", st["h2"]))
    story.append(Paragraph(
        "The existing approaches to plant/soil image assistance have the following limitations:",
        st["body"],
    ))
    for i, t in enumerate([
        "Heavy dependence on manual visual interpretation.",
        "Limited automation in connecting a photo to practical advice.",
        "Classifiers may force a label even when the image is unrelated.",
        "Lack of clear “wrong image” messaging for beginners.",
        "Limited explanation of which Machine Learning algorithm is used.",
        "Limited connection between disease name and practical treatment steps.",
        "Limited connection between soil type and what crops can be grown.",
        "Difficulty in preparing a stable live demo without curated sample images.",
        "Fragmented documentation for clone, install, and run steps.",
        "Limited use of deep embeddings with similarity matching for robust demos.",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph("2.3 Need for the Proposed System", st["h2"]))
    story.append(Paragraph(
        "The above problems indicate the need for an intelligent agricultural image system that "
        "can go beyond simple file upload. The proposed system is designed to analyze leaf and "
        "soil images, identify the closest known class, provide personalized recommendations "
        "(treatment / crops), reject invalid uploads, and support better decision-making. By "
        "combining React.js, FastAPI, TensorFlow/Keras EfficientNetB0 embeddings, OpenCV "
        "heuristics, and curated demo assets, the system aims to provide a centralized and "
        "efficient solution for modern educational and practical agricultural image analysis.",
        st["body"],
    ))

    story.append(Paragraph("2.4 Related Technology Background", st["h2"]))
    story.append(Paragraph(
        "Computer vision for agriculture commonly uses Convolutional Neural Networks because "
        "leaves and soil textures contain local patterns (spots, veins, grain) that CNNs capture "
        "well. Transfer learning with ImageNet-pretrained networks such as EfficientNet reduces "
        "the need to train a huge model from scratch. Similarity search in embedding space is "
        "widely used in image retrieval: two images with similar meaning map to nearby vectors. "
        "AgriTech applies this idea to class prototypes so each prediction is explainable as "
        "“closest known class.”",
        st["body"],
    ))
    story.append(Paragraph(
        "Web integration matters for usability. A model that only runs in a notebook is hard to "
        "demonstrate to non-programmers. Exposing inference through FastAPI and presenting "
        "results in React makes the ML pipeline accessible during seminars and lab evaluations.",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== CHAPTER 3 ==========
    chapter_header(story, st, "3", "REQUIREMENTS")

    story.append(Paragraph(
        "AgriTech requires various software tools and technologies for frontend development, "
        "backend development, and Artificial Intelligence / Machine Learning implementation.",
        st["body"],
    ))
    story.append(Paragraph("3.1 Software Requirements", st["h2"]))

    reqs = [
        ("3.1.1 Operating System",
         "Windows 10/11 (also usable on Linux or macOS).",
         "Provides the environment required for application development and execution."),
        ("3.1.2 Frontend Technology",
         "React.js (Create React App), Axios, React Router, Tailwind-style utility classes.",
         "Used to develop the interactive and user-friendly interface for upload, analysis, "
         "and result display."),
        ("3.1.3 Backend Technology",
         "FastAPI + Uvicorn.",
         "Used to develop REST APIs and handle business logic, file upload, and JSON responses. "
         "Manages communication between the frontend and AI/ML components."),
        ("3.1.4 Programming Languages",
         "JavaScript – frontend development. Python – backend, preprocessing, and ML inference.",
         "Python runs TensorFlow/Keras inference, OpenCV checks, and NumPy similarity scoring."),
        ("3.1.5 Machine Learning Libraries",
         "TensorFlow 2.x, Keras, EfficientNetB0 (ImageNet), OpenCV, NumPy, Pillow, scikit-learn (supporting stack).",
         "Used for deep feature extraction, image preprocessing, and similarity-based class matching."),
        ("3.1.6 Datasets",
         "PlantDoc leaf images; project soil image set (Alluvial, Black, Clay, Red).",
         "Used to build class prototypes (average embeddings) for matching at prediction time."),
        ("3.1.7 Development Environment",
         "Visual Studio Code / Cursor; Python virtual environment (.venv).",
         "Local virtual environment isolates TensorFlow and API dependencies."),
        ("3.1.8 Web Browser",
         "Google Chrome / Microsoft Edge.",
         "Used to run the React app at http://localhost:3000."),
        ("3.1.9 Version Control",
         "Git / GitHub.",
         "Repository: https://github.com/crispyvicky/agritech.git"),
        ("3.1.10 Package Managers",
         "pip (Python), npm (Node.js frontend).",
         "Used to install backend requirements and frontend node_modules."),
    ]
    for head, main, note in reqs:
        story.append(Paragraph(head, st["h3"]))
        story.append(Paragraph(main, st["body"]))
        story.append(Paragraph(note, st["body"]))

    story.append(Paragraph("3.2 Hardware Requirements", st["h2"]))
    for t in [
        "Processor: Intel Core i5 / AMD Ryzen 5 or equivalent (or better).",
        "RAM: 8 GB minimum; 16 GB recommended for TensorFlow.",
        "Storage: 256 GB SSD or above (models and node_modules need space).",
        "Display: HD / Full HD for comfortable demo.",
        "Internet: Required for first-time clone and package install; local demo can run after setup.",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))

    story.append(PageBreak())

    # ========== CHAPTER 4 ==========
    chapter_header(story, st, "4", "DESIGN AND IMPLEMENTATION")

    story.append(Paragraph("4.1 Design", st["h2"]))
    story.append(Paragraph("4.1.1 System Architecture", st["h3"]))
    story.append(Paragraph(
        "The system follows a client–server architecture. The React frontend collects an image "
        "and sends it as multipart form data to the FastAPI backend. The backend saves a "
        "temporary file, runs validation heuristics, extracts an EfficientNetB0 embedding, "
        "compares it with class prototypes, attaches guidance fields, and returns JSON. "
        "Invalid or wrong-type images return a clear error message instead of a forced guess. "
        "Temporary files are deleted after prediction.",
        st["body"],
    ))

    arch = [
        ["Layer", "Responsibility"],
        ["Frontend (React)", "Upload UI, Analyze / Predict actions, result and tip cards"],
        ["API (FastAPI)", "Routes /predict and /predict-soil, CORS, temp file handling"],
        ["Validation", "OpenCV / color heuristics to reject soil↔plant mismatches"],
        ["AI (TensorFlow)", "EfficientNetB0 embeddings + cosine similarity to prototypes"],
        ["Guidance data", "Disease treatments and soil crop / care tips"],
        ["Demo assets", "DEMO_TESTED_IMAGES for accurate live presentation"],
    ]
    t = Table(arch, colWidths=[1.7 * inch, 4.3 * inch])
    t.setStyle(table_style())
    story.append(t)
    story.append(Paragraph("Table 4.1: High-level system layers", st["fig"]))

    story.append(Paragraph("4.1.2 Data Processing Design", st["h3"]))
    story.append(Paragraph(
        "Uploaded images are stored temporarily under temp_uploads/. For embedding inference, "
        "images are loaded with Pillow/OpenCV, resized to 224×224, converted to RGB, "
        "preprocessed with EfficientNet preprocess_input, and passed through EfficientNetB0 "
        "with include_top=False and average pooling. The resulting feature vector is "
        "L2-normalized. Cosine similarity with each class prototype is computed using a "
        "dot product of unit vectors. The highest score becomes the predicted class; the top "
        "three scores are returned for transparency.",
        st["body"],
    ))
    story.append(Paragraph(
        "Confidence is derived from similarity (mapped into a 0–1 range). If the margin between "
        "the best and second-best class is small, or confidence is low, the status may be marked "
        "UNCERTAIN so the UI does not overclaim accuracy.",
        st["body"],
    ))

    story.append(Paragraph("4.1.3 CNN / Embedding Model Design", st["h3"]))
    story.append(Paragraph(
        "Convolutional Neural Networks (CNNs) learn hierarchical visual features. EfficientNetB0 "
        "is a compact CNN architecture pretrained on ImageNet. In AgriTech, the classification "
        "head is removed so the network acts as a feature extractor (embedding model). This "
        "produces a fixed-length vector that represents the visual content of the uploaded photo.",
        st["body"],
    ))
    story.append(Paragraph(
        "Class prototypes are built by averaging embeddings of representative training images "
        "for each plant or soil class and then re-normalizing. At inference time, the query "
        "embedding is matched to the nearest prototype. This design is stable for college demos "
        "and still accepts external photos of the same kind (clear leaf close-ups or clear soil).",
        st["body"],
    ))

    story.append(Paragraph("4.1.4 Machine Learning Algorithm (Clear Description)", st["h3"]))
    story.append(Paragraph(
        "The core Machine Learning algorithm used by AgriTech is:",
        st["body"],
    ))
    story.append(Paragraph(
        "<b>Deep CNN Feature Extraction (EfficientNetB0) + Nearest Prototype Matching "
        "using Cosine Similarity</b>",
        st["body"],
    ))
    story.append(Paragraph("Step-by-step working of the algorithm:", st["body"]))
    for i, t in enumerate([
        "Input image I is validated (leaf vs soil heuristics where applicable).",
        "I is resized to 224×224 and preprocessed for EfficientNet.",
        "EfficientNetB0 (ImageNet weights, no top head) computes embedding vector v.",
        "v is L2-normalized: v ← v / ||v||.",
        "For each class c with prototype p_c, similarity s_c = v · p_c (cosine similarity).",
        "Predicted class = argmax_c s_c; confidence is mapped from the best similarity.",
        "If similarity/margin is too low → reject or mark UNCERTAIN.",
        "Attach treatment tip (plant) or crops/care tips (soil) and return JSON to the UI.",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph(
        "This is a form of metric / similarity-based classification on deep features, rather "
        "than only a single end-to-end softmax classifier for every demo photo. It makes the "
        "pipeline easier to explain in a viva: CNN extracts features; cosine similarity finds "
        "the closest known class; guidance tables add human-readable advice.",
        st["body"],
    ))

    alg = [
        ["Item", "Choice in AgriTech"],
        ["Deep model", "EfficientNetB0 (Keras / TensorFlow, ImageNet)"],
        ["Feature type", "Global average pooled embedding vector"],
        ["Matching method", "Cosine similarity to class prototypes"],
        ["Decision rule", "Nearest prototype (argmax similarity)"],
        ["Uncertainty", "Low similarity / small margin → UNCERTAIN or reject"],
        ["Plant guidance", "treatment_for(label) from treatments.py"],
        ["Soil guidance", "crops + care dictionary per soil class"],
    ]
    t2 = Table(alg, colWidths=[1.8 * inch, 4.2 * inch])
    t2.setStyle(table_style())
    story.append(t2)
    story.append(Paragraph("Table 4.2: Machine Learning algorithm summary", st["fig"]))

    story.append(Paragraph("4.2 Implementation", st["h2"]))
    story.append(Paragraph(
        "Implementation is split into frontend pages, FastAPI routes, and Python scripts under "
        "backend/scripts/. Models and indices are loaded lazily on first request to keep startup "
        "reasonable. CORS is configured so the React app on port 3000 can call the API on port 8000.",
        st["body"],
    ))

    story.append(Paragraph("4.3 Module Implementation", st["h2"]))
    story.append(Paragraph("4.3.1 Plant Disease Module", st["h3"]))
    story.append(Paragraph(
        "Leaf images are matched to PlantDoc-style classes (for example Tomato leaf late blight, "
        "Apple leaf, Corn rust leaf). Healthy vs diseased status is derived from the class name. "
        "When diseased, a short treatment technique is attached. Soil-like or non-leaf images "
        "are rejected with an explicit message asking for a plant leaf image only.",
        st["body"],
    ))
    story.append(Paragraph("4.3.2 Soil Detection Module", st["h3"]))
    story.append(Paragraph(
        "Soil photos are matched to Alluvial, Black, Clay, or Red soil. The API returns suitable "
        "crops (what can be grown) and care tips. Leaf-heavy / green-dominant photos are rejected "
        "so the tool asks for a soil image only.",
        st["body"],
    ))
    story.append(Paragraph("4.3.3 Frontend Modules", st["h3"]))
    story.append(Paragraph(
        "App.js defines routes. AgriDashboard links to the two demo tools. "
        "PlantDiseaseDetection.jsx and SoilPredictor.jsx handle file selection, API calls, "
        "loading state, error display, and result formatting including treatment / crop tips.",
        st["body"],
    ))

    story.append(Paragraph("4.4 User Interface Design", st["h2"]))
    story.append(Paragraph(
        "The landing page presents AgriTech branding and a dashboard of tools. Plant Disease "
        "Detection and Soil Predictor pages keep a simple flow: Upload → Analyze/Predict → Result. "
        "Results show class, confidence, status, and tips. Error messages from the API are shown "
        "directly so wrong uploads are obvious during a demo.",
        st["body"],
    ))

    story.append(Paragraph("4.5 System Integration", st["h2"]))
    story.append(Paragraph(
        "System integration combines all modules into one functional platform. The React frontend "
        "communicates with FastAPI through REST APIs. AI/ML scripts are imported from "
        "backend/scripts. Processed results are returned to the frontend and displayed through "
        "result cards, providing users with a complete plant/soil image assistance experience.",
        st["body"],
    ))
    story.append(Paragraph("4.5.1 Frontend and Backend Integration", st["h3"]))
    story.append(Paragraph(
        "Axios posts FormData with the selected file to ENDPOINTS.PREDICT_DISEASE (/predict) "
        "or the soil endpoint (/predict-soil). The backend returns JSON. If error or "
        "invalid_image is present, the UI shows the message; otherwise it renders the prediction.",
        st["body"],
    ))
    story.append(Paragraph("4.5.2 AI/ML Model Integration", st["h3"]))
    story.append(Paragraph(
        "load_plantdoc_predictor() and predict_soil_from_path() integrate the embedding pipeline. "
        "EfficientNetB0 weights are loaded via Keras. Prototype indices are built or loaded from "
        "disk when available. Treatments and soil_info dictionaries enrich the ML output with "
        "human-readable recommendations.",
        st["body"],
    ))

    story.append(Paragraph("4.6 Detailed Working Flow (College Explanation)", st["h2"]))
    story.append(Paragraph(
        "This subsection explains the complete journey of one prediction in simple academic language.",
        st["body"],
    ))
    story.append(Paragraph("4.6.1 Plant Disease Path", st["h3"]))
    story.append(Paragraph(
        "When a user uploads a leaf image on the Plant Disease Detection page, the browser creates "
        "a FormData object and posts it to POST /predict. FastAPI receives the UploadFile, writes "
        "bytes to temp_uploads/, and calls predict_disease(file_path). The predictor first checks "
        "whether the photo looks like soil/ground using color heuristics (earth-tone ratio vs green "
        "ratio). If it looks like soil, the API returns status=invalid_image with a message asking "
        "for a plant leaf only. Otherwise, EfficientNetB0 computes embedding v. Cosine similarities "
        "against all plant class prototypes are sorted. The best class name becomes the prediction. "
        "If the best similarity is too low, the system rejects the image as “not a clear leaf.” "
        "If the margin between top-1 and top-2 is small, status becomes UNCERTAIN. Otherwise status "
        "is HEALTHY or DISEASED based on a healthy-class set. treatment_for(best_name) adds a short "
        "treatment technique string. The JSON is returned; the UI shows class, confidence percent, "
        "status color, top predictions, and the treatment tip.",
        st["body"],
    ))
    story.append(Paragraph("4.6.2 Soil Path", st["h3"]))
    story.append(Paragraph(
        "When a user uploads a soil image, the frontend posts to POST /predict-soil. The soil "
        "embedder rejects leaf-like green-dominant photos. Valid soil photos are embedded and "
        "matched to Alluvial, Black, Clay, or Red prototypes. The response includes prediction, "
        "confidence, notes, crops (what can be grown), and care tips. This turns a soil label into "
        "actionable farming guidance suitable for presentation.",
        st["body"],
    ))
    story.append(Paragraph("4.6.3 Why This Algorithm Fits a College Project", st["h3"]))
    story.append(Paragraph(
        "Using a pretrained CNN as a feature extractor is a standard transfer-learning pattern. "
        "Students can explain: (1) CNN layers detect edges/textures/patterns, (2) the embedding "
        "summarizes the image, (3) cosine similarity is a well-known distance/similarity measure, "
        "(4) prototypes are class centroids in feature space, (5) business rules (reject / uncertain / "
        "tips) make the system usable. This is easier to defend in a viva than a black-box label alone.",
        st["body"],
    ))

    story.append(Paragraph("4.7 Soil Crop Guidance Summary", st["h2"]))
    crops = [
        ["Soil type", "Example crops that can be grown"],
        ["Alluvial soil", "Rice, Wheat, Corn, Sugarcane, Cotton"],
        ["Black Soil", "Cotton, Wheat, Jowar, Linseed, Tobacco"],
        ["Clay soil", "Rice, Wheat, Barley, Oats"],
        ["Red soil", "Millet, Groundnut, Potato, Tobacco, Pulses"],
    ]
    tc = Table(crops, colWidths=[1.6 * inch, 4.4 * inch])
    tc.setStyle(table_style())
    story.append(tc)
    story.append(Paragraph("Table 4.3: Soil types and suitable crops (system guidance)", st["fig"]))

    story.append(Paragraph("4.8 Limitations (Honest Scope)", st["h2"]))
    for t in [
        "Accuracy depends on photo quality (blur, extreme lighting, mixed backgrounds hurt results).",
        "The system is a decision-support demo, not a replacement for a certified agronomist.",
        "Soil classes are limited to four types used in the project dataset.",
        "External random images may be rejected or marked uncertain — this is intentional.",
        "Treatment tips are educational guidelines, not prescription medical/agrochemical advice.",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))
    story.append(PageBreak())

    # ========== CHAPTER 5 ==========
    chapter_header(story, st, "5", "CODE")

    story.append(Paragraph(
        "Selected source fragments are shown below to illustrate the main flow (not the entire "
        "codebase). Full source lives under backend/ and frontend/.",
        st["body"],
    ))
    story.append(Paragraph("5.1 Source Code", st["h2"]))

    story.append(Paragraph("App.js", st["code_title"]))
    story.append(Preformatted(
        """import PlantDiseaseDetection from './pages/PlantDiseaseDetection';
import SoilPredictor from './pages/SoilPredictor';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/disease-detection"
               element={<PlantDiseaseDetection />} />
        <Route path="/SoilPredictor"
               element={<SoilPredictor />} />
        <Route path="/" element={<HomeWithDashboard />} />
      </Routes>
    </Router>
  );
}""",
        st["code"],
    ))

    story.append(Paragraph("PlantDiseaseDetection.jsx (API call)", st["code_title"]))
    story.append(Preformatted(
        """const formData = new FormData();
formData.append('file', selectedImage);
const response = await axios.post(
  ENDPOINTS.PREDICT_DISEASE, formData,
  { headers: { 'Content-Type': 'multipart/form-data' } }
);
if (data.error || data.status === 'invalid_image') {
  setError(data.error || 'Please upload a plant leaf image only.');
} else {
  setResult(data);  // class, confidence, status, treatment
}""",
        st["code"],
    ))

    story.append(PageBreak())
    story.append(Paragraph("main.py (API routes)", st["code_title"]))
    story.append(Preformatted(
        """@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    predict_func = load_plantdoc_predictor()
    # save upload temporarily
    result = predict_func(file_path)
    os.remove(file_path)
    return result

@app.post("/predict-soil")
async def predict_soil(file: UploadFile = File(...)):
    from predict_soil_embed import predict_soil_from_path
    return predict_soil_from_path(file_path)""",
        st["code"],
    ))

    story.append(Paragraph("predict_plantdoc.py (algorithm core)", st["code_title"]))
    story.append(Preformatted(
        """# 1) Reject soil-like photos
if _looks_like_soil_not_plant(image_path):
    return {"error": "Please upload a plant leaf image only.",
            "status": "invalid_image"}

# 2) Embed query image with EfficientNetB0
q = _embed_path(Path(image_path))   # L2-normalized vector

# 3) Cosine similarity vs each class prototype
scores = [(name, float(np.dot(q, proto))) for name, proto in index.items()]
scores.sort(key=lambda x: -x[1])
best_name, best_sim = scores[0]

# 4) Attach treatment tip
treatment = treatment_for(best_name)
return {"class": best_name, "confidence": conf,
        "status": status, "treatment": treatment}""",
        st["code"],
    ))

    story.append(Paragraph("EfficientNetB0 embedding load", st["code_title"]))
    story.append(Preformatted(
        """_embed_model = EfficientNetB0(
    include_top=False, weights="imagenet",
    pooling="avg", input_shape=(224, 224, 3)
)
vec = model.predict(preprocess(image), verbose=0)[0]
vec = vec / (np.linalg.norm(vec) + 1e-8)""",
        st["code"],
    ))

    story.append(PageBreak())
    story.append(Paragraph("Soil guidance dictionary (excerpt)", st["code_title"]))
    story.append(Preformatted(
        '''soil_info = {
  "Alluvial soil": {
    "crops": ["Rice", "Wheat", "Corn", "Sugarcane", "Cotton"],
    "care": ["Ensure proper drainage", "Add organic matter"]
  },
  "Black Soil": {
    "crops": ["Cotton", "Wheat", "Jowar", "Linseed", "Tobacco"],
    "care": ["Improve drainage", "Add organic compost"]
  },
  "Clay soil": {
    "crops": ["Rice", "Wheat", "Barley", "Oats"],
    "care": ["Improve drainage", "Avoid working when wet"]
  },
  "Red soil": {
    "crops": ["Millet", "Groundnut", "Potato", "Pulses"],
    "care": ["Add lime if acidic", "Regular fertilization"]
  },
}''',
        st["code"],
    ))

    story.append(Paragraph("Treatment tip example", st["code_title"]))
    story.append(Preformatted(
        '''TREATMENTS = {
  "Tomato leaf late blight":
    "Remove and destroy infected plants quickly. Keep foliage dry; "
    "apply late-blight fungicide. Rotate next year.",
  "Corn rust leaf":
    "Plant resistant varieties; fungicide can help if rust appears early.",
  # ... other PlantDoc classes ...
}''',
        st["code"],
    ))

    story.append(PageBreak())
    story.append(Paragraph("predict_soil_embed.py (reject leaf on soil tool)", st["code_title"]))
    story.append(Preformatted(
        """def predict_soil_from_path(image_path: str) -> dict:
    # Reject green/leaf-heavy photos
    if looks_like_plant_not_soil(image):
        return {
          "error": "This does not look like a soil photo. "
                   "Please upload a soil image only "
                   "(not leaves or plants).",
          "status": "invalid_image",
        }
    # Embed + match soil prototypes (Alluvial/Black/Clay/Red)
    pred, conf = nearest_soil_class(embed(image_path))
    info = soil_info[pred]
    return {
      "prediction": pred,
      "confidence": conf,
      "crops": info["crops"],
      "care": info["care"],
      "notes": info["notes"],
    }""",
        st["code"],
    ))

    story.append(Paragraph("start.py (server entry)", st["code_title"]))
    story.append(Preformatted(
        """import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)""",
        st["code"],
    ))

    story.append(Paragraph(
        "Additional implementation files (not fully pasted here to keep the report readable): "
        "backend/scripts/predict_plantdoc.py, predict_soil_embed.py, treatments.py, "
        "frontend/src/pages/SoilPredictor.jsx, frontend/src/config/api.js, backend/main.py.",
        st["body"],
    ))

    story.append(PageBreak())
    story.append(Paragraph("5.2 Screenshots / Demo Images of Application", st["h2"]))
    story.append(Paragraph(
        "Verified demo images used for accurate results are stored in "
        "AgriSync\\DEMO_TESTED_IMAGES. Representative samples used during testing:",
        st["body"],
    ))

    samples = [
        (DEMO / "plant_disease" / "01_tomato_late_blight.jpg",
         "Fig 5.1 Plant Disease — Tomato late blight (diseased + treatment)"),
        (DEMO / "plant_disease" / "02_apple_leaf_healthy.jpg",
         "Fig 5.2 Plant Disease — Apple leaf (healthy)"),
        (DEMO / "plant_disease" / "03_corn_rust_leaf.jpg",
         "Fig 5.3 Plant Disease — Corn rust leaf (diseased)"),
    ]
    for path, cap in samples:
        for block in maybe_image(path, caption=cap, st=st):
            story.append(block)
        story.append(Paragraph(
            "During the demo, open Plant Disease Detection, click Upload image, select this file "
            "from DEMO_TESTED_IMAGES\\plant_disease, then click Analyze. Read the class name, "
            "confidence, status, and treatment tip (for diseased samples).",
            st["body"],
        ))
        story.append(PageBreak())

    soil_samples = [
        (DEMO / "soil" / "01_alluvial_soil.jpg", "Fig 5.4 Soil — Alluvial soil"),
        (DEMO / "soil" / "03_black_soil.jpg", "Fig 5.5 Soil — Black soil"),
        (DEMO / "soil" / "05_clay_soil.jpg", "Fig 5.6 Soil — Clay soil"),
        (DEMO / "soil" / "06_red_soil.jpg", "Fig 5.7 Soil — Red soil"),
    ]
    for path, cap in soil_samples:
        for block in maybe_image(path, width=4.4 * inch, caption=cap, st=st):
            story.append(block)
        story.append(PageBreak())

    story.append(Paragraph(
        "Fig 5.8 Application flow: open http://localhost:3000 → Plant Disease Detection "
        "or Soil Detection → Upload image from DEMO_TESTED_IMAGES → Analyze / Predict → "
        "read class, confidence, and tips.",
        st["fig"],
    ))
    story.append(PageBreak())

    # ========== CHAPTER 6 ==========
    chapter_header(story, st, "6", "RESULTS &amp; CONCLUSION")

    story.append(Paragraph("6.1 RESULTS", st["h2"]))
    story.append(Paragraph(
        "The proposed AgriTech system was designed and implemented to provide an intelligent "
        "and user-friendly platform for plant disease detection and soil classification. The "
        "system successfully integrates React.js, FastAPI, TensorFlow/Keras EfficientNetB0 "
        "embeddings, OpenCV validation heuristics, and guidance dictionaries.",
        st["body"],
    ))
    story.append(Paragraph(
        "The plant module returns disease/healthy class labels with confidence and treatment "
        "tips for diseased leaves. The soil module returns soil type with crops that can be "
        "grown and care tips. Wrong-image uploads return clear guidance messages. Overall, "
        "the system achieves its objective of simplifying agricultural image analysis for "
        "demonstration and educational use.",
        st["body"],
    ))

    results = [
        ["Tool", "Sample image", "Expected result"],
        ["Plant", "01_tomato_late_blight.jpg", "Tomato late blight + treatment tip"],
        ["Plant", "02_apple_leaf_healthy.jpg", "Apple leaf (healthy)"],
        ["Plant", "03_corn_rust_leaf.jpg", "Corn rust leaf (diseased)"],
        ["Soil", "01_alluvial_soil.jpg", "Alluvial + crops / care tips"],
        ["Soil", "03_black_soil.jpg", "Black Soil + crops / care tips"],
        ["Soil", "05_clay_soil.jpg", "Clay soil + crops / care tips"],
        ["Soil", "06_red_soil.jpg", "Red soil + crops / care tips"],
    ]
    t3 = Table(results, colWidths=[0.8 * inch, 2.2 * inch, 3.0 * inch])
    t3.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)
    story.append(Paragraph("Table 6.1: Tested demo samples and expected outputs", st["fig"]))

    story.append(Paragraph("6.1.1 How the System Works (End-to-End Summary)", st["h3"]))
    for i, t in enumerate([
        "User opens Plant Disease or Soil Detection in the browser.",
        "User selects an image (preferably from DEMO_TESTED_IMAGES for demos).",
        "Frontend posts the file to /predict or /predict-soil.",
        "Backend validates image type (leaf vs soil).",
        "EfficientNetB0 extracts an embedding; cosine similarity finds the nearest class.",
        "Guidance (treatment or crops/care) is attached.",
        "JSON is returned and shown in the UI; temp file is deleted.",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph("6.1.2 Observation During Testing", st["h3"]))
    story.append(Paragraph(
        "During testing with curated demo images, plant samples such as tomato late blight, "
        "apple leaf (healthy), and corn rust leaf produced consistent class labels with treatment "
        "tips for diseased cases. Soil samples for Alluvial, Black, Clay, and Red returned the "
        "expected class along with crop lists. Cross-tool uploads (soil into plant tool and leaf "
        "into soil tool) correctly triggered rejection messages. These observations support the "
        "claim that the system is suitable for live college demonstration when DEMO_TESTED_IMAGES "
        "are used.",
        st["body"],
    ))
    story.append(Paragraph(
        "External images can still be used: a clear close-up of a single leaf generally works "
        "better than a wide farm scene; a clear soil surface works better than a photo dominated "
        "by grass or tools. Low-confidence / UNCERTAIN outputs should be interpreted as “try a "
        "clearer photo,” not as a forced diagnosis.",
        st["body"],
    ))

    story.append(Paragraph("6.2 CONCLUSION", st["h2"]))
    story.append(Paragraph(
        "AgriTech successfully provides a centralized and intelligent platform for managing "
        "plant disease and soil image analysis. The system combines modern web technologies "
        "with a clearly defined Machine Learning algorithm—EfficientNetB0 deep embeddings with "
        "cosine-similarity prototype matching—to help users identify leaf problems and soil "
        "types and receive practical treatment and crop guidance.",
        st["body"],
    ))
    story.append(Paragraph(
        "Wrong-image rejection keeps the demo honest when unrelated photos are tried. The "
        "interactive UI presents results in a simple and understandable manner. Overall, the "
        "project achieves its main objective of simplifying agricultural image assistance "
        "through a user-friendly platform suitable for college-level evaluation.",
        st["body"],
    ))
    story.append(Paragraph(
        "The system can be further enhanced in the future by adding more plant classes, "
        "improving soil accuracy on difficult lookalikes, localized treatment guides, "
        "multilingual tips, and optional mobile camera capture for field use.",
        st["body"],
    ))

    story.append(Paragraph("6.3 Future Enhancements", st["h2"]))
    for i, t in enumerate([
        "Expand plant disease classes and regional crop-specific tips.",
        "Improve soil discrimination between visually similar clay/red samples.",
        "Add optional camera capture for field use on mobile browsers.",
        "Provide PDF export of a single prediction report for farmers/students.",
        "Add unit/integration tests for reject rules and API contracts.",
        "Package a one-click demo script for Windows presentation machines.",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))
    story.append(PageBreak())

    # ========== REFERENCES ==========
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("REFERENCES", st["chapter_title"]))
    refs = [
        "React Documentation, “React – A JavaScript library for building user interfaces.” https://react.dev/ — 2026",
        "FastAPI Documentation, “FastAPI – Modern Python web framework.” https://fastapi.tiangolo.com/ — 2026",
        "TensorFlow Documentation, “TensorFlow – An end-to-end platform for machine learning.” https://www.tensorflow.org/ — 2026",
        "Keras Documentation, “Keras API – Deep learning for humans.” https://keras.io/ — 2026",
        "Tan, M. &amp; Le, Q., “EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks.” ICML — 2019",
        "PlantDoc Dataset – Plant disease detection images for computer vision research.",
        "OpenCV Documentation, “OpenCV – Open Source Computer Vision Library.” https://docs.opencv.org/ — 2026",
        "NumPy Developers, “NumPy Documentation.” https://numpy.org/doc/stable/ — 2026",
        "Uvicorn Documentation, “Uvicorn – ASGI server.” https://www.uvicorn.org/ — 2026",
        "Python Software Foundation, “Python Documentation.” https://docs.python.org/3/ — 2026",
        "scikit-learn Developers, “Scikit-learn – Machine Learning in Python.” https://scikit-learn.org/stable/ — 2026",
        "MDN Web Docs, “Using FormData objects.” https://developer.mozilla.org/ — 2026",
        "GitHub, AgriSync repository. https://github.com/crispyvicky/agritech.git — 2026",
    ]
    for i, r in enumerate(refs, start=1):
        story.append(Paragraph(f"{i}. {r}", st["ref"]))

    story.append(PageBreak())

    # ========== APPENDIX ==========
    story.append(Paragraph("APPENDIX", st["chapter_title"]))

    story.append(Paragraph("APPENDIX – A", st["h2"]))
    story.append(Paragraph("System Configuration", st["h3"]))
    story.append(Paragraph(
        "The project was developed and tested on a computer-based system. The main software "
        "and hardware configuration used for implementation is listed below.",
        st["body"],
    ))
    story.append(Paragraph("<b>Hardware Configuration</b>", st["h3"]))
    for t in [
        "Processor: Intel Core i5 / AMD Ryzen 5 or equivalent",
        "RAM: 8 GB or above (16 GB recommended for TensorFlow)",
        "Storage: 256 GB SSD or above",
        "Display: Standard HD / Full HD Display",
        "Internet: Required for development and first package install",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))

    story.append(Paragraph("<b>Software Configuration</b>", st["h3"]))
    for t in [
        "Operating System: Windows 10/11",
        "Frontend Technology: React.js",
        "Backend Technology: FastAPI + Uvicorn",
        "Programming Languages: JavaScript, Python",
        "Development Environment: Visual Studio Code / Cursor",
        "Machine Learning: TensorFlow, Keras, EfficientNetB0, OpenCV, NumPy",
        "Algorithm: CNN embedding + cosine similarity prototype matching",
        "Web Browser: Google Chrome / Microsoft Edge",
        "Version Control: Git / GitHub",
        "Package managers: pip, npm",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))

    story.append(Paragraph("APPENDIX – B", st["h2"]))
    story.append(Paragraph("Dataset Information", st["h3"]))
    story.append(Paragraph(
        "The system uses plant leaf images (PlantDoc-style classes) and soil images for "
        "building class prototypes and evaluating predictions. Major data categories:",
        st["body"],
    ))
    for i, t in enumerate([
        "Plant leaf images (healthy and diseased classes)",
        "Soil images (Alluvial, Black, Clay, Red)",
        "Class prototype index (average embeddings per class)",
        "Treatment tip strings per plant class",
        "Crop and care tip lists per soil class",
        "Verified demo copies under DEMO_TESTED_IMAGES",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph(
        "Demo folder path: AgriSync\\DEMO_TESTED_IMAGES\\plant_disease\\ and "
        "AgriSync\\DEMO_TESTED_IMAGES\\soil\\",
        st["body"],
    ))

    story.append(Paragraph("APPENDIX – C", st["h2"]))
    story.append(Paragraph("Major Functional Modules", st["h3"]))
    for i, t in enumerate([
        "User opens landing dashboard and selects a tool",
        "Plant Disease Detection — upload leaf → analyze → class / status / treatment",
        "Soil Detection — upload soil → predict → soil type / crops / care",
        "Wrong-image rejection messages for plant and soil tools",
        "Backend health endpoints (/health, /healthz)",
        "Temporary upload cleanup after prediction",
        "Demo image pack for accurate presentation results",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph("APPENDIX – D", st["h2"]))
    story.append(Paragraph("How to Run (Quick Reference)", st["h3"]))
    story.append(Preformatted(
        """# Backend
cd AgriSync\\backend
$env:PORT="8000"
$env:PYTHONUTF8="1"
.\\.venv\\Scripts\\python.exe start.py

# Frontend
cd AgriSync\\frontend
npm start
# open http://localhost:3000

# Full beginner guide:
# docs\\AgriTech_Setup_and_Demo_Guide.pdf""",
        st["code"],
    ))

    story.append(Paragraph("APPENDIX – E", st["h2"]))
    story.append(Paragraph("Viva / Oral Explanation Points", st["h3"]))
    story.append(Paragraph(
        "Students can use the following points when explaining the project orally:",
        st["body"],
    ))
    for i, t in enumerate([
        "Problem: farmers/students need quick help reading leaf disease and soil type from photos.",
        "Solution: AgriTech web app with two tools — Plant Disease Detection and Soil Detection.",
        "ML algorithm: EfficientNetB0 CNN embeddings + cosine similarity to class prototypes.",
        "Why not only guess labels: wrong images are rejected; uncertain cases are marked.",
        "Plant output: class, confidence, HEALTHY/DISEASED, treatment technique tip.",
        "Soil output: soil type, confidence, crops that can grow, care tips.",
        "Stack: React frontend, FastAPI backend, TensorFlow/Keras, OpenCV, NumPy.",
        "Demo reliability: use DEMO_TESTED_IMAGES folder for accurate live results.",
        "Clone URL: https://github.com/crispyvicky/agritech.git",
        "Setup details: see AgriTech_Setup_and_Demo_Guide.pdf for beginner steps.",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph("APPENDIX – F", st["h2"]))
    story.append(Paragraph("API Response Fields (for documentation)", st["h3"]))
    api_fields = [
        ["Field", "Plant / Soil meaning"],
        ["class / prediction", "Predicted label name"],
        ["confidence", "Score derived from similarity (0–1)"],
        ["status", "HEALTHY / DISEASED / UNCERTAIN / invalid_image"],
        ["treatment", "Plant: short treatment technique text"],
        ["crops", "Soil: list of suitable crops"],
        ["care", "Soil: care tip list"],
        ["error", "Human-readable rejection or failure message"],
        ["top_predictions", "Plant: alternate close classes"],
        ["engine", "Identifier of matching engine used"],
    ]
    tf = Table(api_fields, colWidths=[1.7 * inch, 4.3 * inch])
    tf.setStyle(table_style())
    story.append(tf)
    story.append(Paragraph("Table A.1: Important API response fields", st["fig"]))

    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph("— End of Document —", st["fig"]))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    OUT_ROOT.write_bytes(OUT_DOCS.read_bytes())
    print(f"Wrote {OUT_DOCS}")
    print(f"Wrote {OUT_ROOT}")


if __name__ == "__main__":
    build()
