"""
Beginner guide PDF: clone, install, run, present, which images to upload.
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
OUT = DOCS / "AgriTech_Setup_and_Demo_Guide.pdf"
OUT_ROOT = ROOT / "AgriTech_Setup_and_Demo_Guide.pdf"
DEMO = ROOT / "DEMO_TESTED_IMAGES"
REPO = "https://github.com/crispyvicky/agritech.git"


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=base["Title"], fontName="Times-Bold",
            fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=8,
        ),
        "sub": ParagraphStyle(
            "S", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Times-Bold",
            fontSize=13, leading=17, spaceBefore=12, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Times-Bold",
            fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "Bu", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=14, leftIndent=16, spaceAfter=3,
        ),
        "num": ParagraphStyle(
            "N", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=14, leftIndent=16, spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "C", fontName="Courier", fontSize=8.5, leading=11,
            leftIndent=4, spaceBefore=3, spaceAfter=8,
            backColor=colors.HexColor("#f4f4f4"),
        ),
        "warn": ParagraphStyle(
            "W", parent=base["Normal"], fontName="Times-Bold",
            fontSize=10.5, leading=14, textColor=colors.HexColor("#333333"),
            spaceBefore=4, spaceAfter=6,
        ),
        "fig": ParagraphStyle(
            "F", fontName="Times-Italic", fontSize=9.5,
            alignment=TA_CENTER, spaceAfter=10,
        ),
    }


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.drawCentredString(A4[0] / 2, 0.55 * inch, f"{doc.page}")
    canvas.restoreState()


def maybe_image(path, width=3.2 * inch, caption="", st=None):
    st = st or styles()
    if not path.exists():
        return []
    img = Image(str(path), width=width, height=width * 0.7, kind="proportional")
    img.hAlign = "CENTER"
    items = [img]
    if caption:
        items.append(Paragraph(caption, st["fig"]))
    return items


def build():
    st = styles()
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=0.95 * inch, rightMargin=0.95 * inch,
        topMargin=0.8 * inch, bottomMargin=0.7 * inch,
        title="AgriTech Setup and Demo Guide", author="AgriTech",
    )
    story = []

    story.append(Spacer(1, 0.6 * inch))
    story.append(Paragraph("AGRITECH", st["title"]))
    story.append(Paragraph(
        "Beginner Guide: Clone · Install · Run · Present",
        st["sub"],
    ))
    story.append(Paragraph(
        "Clean step-by-step instructions for first-time users",
        st["sub"],
    ))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        f"Repository: <font face='Courier'>{REPO}</font>",
        st["sub"],
    ))
    story.append(Paragraph(
        "Demo images folder: <font face='Courier'>AgriSync\\DEMO_TESTED_IMAGES</font>",
        st["sub"],
    ))
    story.append(PageBreak())

    # 1 Before you start
    story.append(Paragraph("1. Before You Start (What You Need)", st["h1"]))
    story.append(Paragraph(
        "This guide is for beginners. Follow the steps in order. You will clone the project "
        "from GitHub, install dependencies, start two terminals (backend + frontend), open "
        "the website, and upload tested demo images.",
        st["body"],
    ))
    story.append(Paragraph("Install these once on your PC:", st["body"]))
    for t in [
        "Git — https://git-scm.com/downloads",
        "Python 3.10 or 3.11 (64-bit) — https://www.python.org/downloads/  (tick “Add Python to PATH”)",
        "Node.js LTS (includes npm) — https://nodejs.org/",
        "Google Chrome or Microsoft Edge",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))
    story.append(Paragraph(
        "Recommended: 8 GB RAM or more (TensorFlow needs memory).",
        st["warn"],
    ))

    # 2 Clone
    story.append(Paragraph("2. How to Clone This Repository", st["h1"]))
    story.append(Paragraph("2.1 Open a terminal", st["h2"]))
    story.append(Paragraph(
        "On Windows: press Win key, type PowerShell, open Windows PowerShell. "
        "Or open Terminal inside VS Code / Cursor.",
        st["body"],
    ))
    story.append(Paragraph("2.2 Go to your Desktop (or any folder you like)", st["h2"]))
    story.append(Preformatted(
        r"""cd $env:USERPROFILE\Desktop""",
        st["code"],
    ))
    story.append(Paragraph("2.3 Clone AgriSync", st["h2"]))
    story.append(Preformatted(
        f"""git clone {REPO}
cd AgriSync""",
        st["code"],
    ))
    story.append(Paragraph(
        "After this you should see folders such as backend, frontend, DEMO_TESTED_IMAGES, and docs.",
        st["body"],
    ))
    story.append(Paragraph(
        "If you already have the project (for example on Desktop\\agri\\AgriSync), "
        "skip cloning and just cd into that AgriSync folder.",
        st["body"],
    ))

    # 3 Install
    story.append(Paragraph("3. Install (First Time Only)", st["h1"]))
    story.append(Paragraph("3.1 Backend (Python + AI)", st["h2"]))
    story.append(Paragraph(
        "Create a virtual environment and install packages. This may take several minutes "
        "because TensorFlow is large.",
        st["body"],
    ))
    story.append(Preformatted(
        r"""cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install reportlab
cd ..""",
        st["code"],
    ))
    story.append(Paragraph(
        "If Activate.ps1 is blocked, run once: "
        "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned",
        st["body"],
    ))

    story.append(Paragraph("3.2 Frontend (React)", st["h2"]))
    story.append(Preformatted(
        r"""cd frontend
npm install
cd ..""",
        st["code"],
    ))
    story.append(Paragraph(
        "Wait until npm finishes without red errors. You only need this once (or after package changes).",
        st["body"],
    ))
    story.append(PageBreak())

    # 4 Run
    story.append(Paragraph("4. How to Run Cleanly (Every Demo)", st["h1"]))
    story.append(Paragraph(
        "You need TWO terminals. Keep both open while you use the website.",
        st["warn"],
    ))

    story.append(Paragraph("4.1 Terminal 1 — Start Backend (port 8000)", st["h2"]))
    story.append(Preformatted(
        r"""cd path\to\AgriSync\backend
$env:PORT="8000"
$env:PYTHONUTF8="1"
.\.venv\Scripts\python.exe start.py""",
        st["code"],
    ))
    story.append(Paragraph(
        "Wait until you see the API starting / Uvicorn running. First start may load models "
        "and take longer. Test in browser: http://localhost:8000/health — should say API is running.",
        st["body"],
    ))

    story.append(Paragraph("4.2 Terminal 2 — Start Frontend (port 3000)", st["h2"]))
    story.append(Preformatted(
        r"""cd path\to\AgriSync\frontend
npm start""",
        st["code"],
    ))
    story.append(Paragraph(
        "Browser should open http://localhost:3000. If not, open that URL yourself.",
        st["body"],
    ))

    story.append(Paragraph("4.3 Stop cleanly when finished", st["h2"]))
    story.append(Paragraph(
        "In each terminal press Ctrl+C. Do not close only the browser if you want to free the ports.",
        st["body"],
    ))

    # 5 Present
    story.append(Paragraph("5. How to Present (Simple Script)", st["h1"]))
    story.append(Paragraph(
        "Say this in about 2–3 minutes while clicking:",
        st["body"],
    ))
    for i, t in enumerate([
        "AgriTech is a web app that helps detect plant leaf diseases and classify soil from photos.",
        "It uses a Machine Learning algorithm: EfficientNetB0 (CNN) embeddings + cosine similarity matching.",
        "Open Plant Disease Detection → upload a leaf → Analyze → show class, confidence, HEALTHY/DISEASED, and treatment tip.",
        "Open Soil Detection → upload soil → Predict → show soil type and which crops can grow + care tips.",
        "Optional: swap images (soil into plant / leaf into soil) to show the “upload correct image only” message.",
        "Mention demo images are pre-tested in DEMO_TESTED_IMAGES for accurate live results.",
    ], start=1):
        story.append(Paragraph(f"{i}. {t}", st["num"]))

    story.append(Paragraph("5.1 What the ML algorithm is (one sentence for viva)", st["h2"]))
    story.append(Paragraph(
        "“We extract a deep feature vector from the photo using EfficientNetB0 pretrained on "
        "ImageNet, then match it to the nearest class prototype with cosine similarity, and "
        "finally attach treatment or crop advice.”",
        st["body"],
    ))
    story.append(PageBreak())

    # 6 Images
    story.append(Paragraph("6. Which Images to Upload (Use These)", st["h1"]))
    story.append(Paragraph(
        "For the most accurate demo results, upload images from this folder only:",
        st["body"],
    ))
    story.append(Preformatted(
        r"""AgriSync\DEMO_TESTED_IMAGES\
  plant_disease\
  soil\
  README.txt""",
        st["code"],
    ))
    story.append(Paragraph(
        "Full path on a typical machine after clone:",
        st["body"],
    ))
    story.append(Preformatted(
        "...\\AgriSync\\DEMO_TESTED_IMAGES\\plant_disease\\\n"
        "...\\AgriSync\\DEMO_TESTED_IMAGES\\soil\\",
        st["code"],
    ))

    story.append(Paragraph("6.1 Plant Disease Detection — upload from plant_disease\\", st["h2"]))
    plant_rows = [
        ["File", "What you should see"],
        ["01_tomato_late_blight.jpg", "Tomato late blight · DISEASED · treatment tip"],
        ["02_apple_leaf_healthy.jpg", "Apple leaf · HEALTHY"],
        ["03_corn_rust_leaf.jpg", "Corn rust leaf · DISEASED"],
    ]
    t = Table(plant_rows, colWidths=[2.4 * inch, 3.6 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("6.2 Soil Detection — upload from soil\\", st["h2"]))
    soil_rows = [
        ["File", "What you should see"],
        ["01_alluvial_soil.jpg / 02_...", "Alluvial soil + crops / care"],
        ["03_black_soil.jpg / 04_...", "Black Soil + crops / care"],
        ["05_clay_soil.jpg", "Clay soil + crops / care"],
        ["06_red_soil.jpg", "Red soil + crops / care"],
    ]
    t2 = Table(soil_rows, colWidths=[2.4 * inch, 3.6 * inch])
    t2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)

    story.append(Paragraph("6.3 Wrong-image demo (optional, impressive)", st["h2"]))
    for t in [
        "Put a soil photo into Plant Disease → should say upload plant leaf only.",
        "Put a leaf photo into Soil Detection → should say upload soil only.",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))

    story.append(Paragraph("6.4 Can I upload my own photos?", st["h2"]))
    story.append(Paragraph(
        "Yes — external images can work if they are clear close-up leaf photos for the plant "
        "tool, or clear soil surface photos for the soil tool. For a graded presentation, "
        "prefer DEMO_TESTED_IMAGES so results stay reliable.",
        st["body"],
    ))
    story.append(PageBreak())

    # Sample previews
    story.append(Paragraph("7. Quick Visual Preview of Demo Images", st["h1"]))
    for block in maybe_image(
        DEMO / "plant_disease" / "01_tomato_late_blight.jpg",
        caption="Plant demo: 01_tomato_late_blight.jpg", st=st,
    ):
        story.append(block)
    for block in maybe_image(
        DEMO / "plant_disease" / "02_apple_leaf_healthy.jpg",
        caption="Plant demo: 02_apple_leaf_healthy.jpg", st=st,
    ):
        story.append(block)
    for block in maybe_image(
        DEMO / "soil" / "01_alluvial_soil.jpg",
        caption="Soil demo: 01_alluvial_soil.jpg", st=st,
    ):
        story.append(block)
    for block in maybe_image(
        DEMO / "soil" / "03_black_soil.jpg",
        caption="Soil demo: 03_black_soil.jpg", st=st,
    ):
        story.append(block)

    story.append(PageBreak())

    # Troubleshooting
    story.append(Paragraph("8. Troubleshooting (Beginner Fixes)", st["h1"]))
    tips = [
        ("Port already in use",
         "Close old terminals, or stop the process using port 8000/3000, then start again."),
        ("npm start fails",
         "Delete frontend\\node_modules and run npm install again inside frontend."),
        ("Backend import / TensorFlow error",
         "Activate .venv and re-run pip install -r requirements.txt."),
        ("Frontend cannot predict",
         "Confirm backend health at http://localhost:8000/health first."),
        ("Weird plant result / low confidence",
         "Use DEMO_TESTED_IMAGES\\plant_disease files; use a clear single-leaf photo."),
        ("Prediction slow first time",
         "Normal — models load on first request. Wait once, then retry."),
    ]
    for title, text in tips:
        story.append(Paragraph(f"<b>{title}</b>", st["h2"]))
        story.append(Paragraph(text, st["body"]))

    story.append(Paragraph("9. Related Documents", st["h1"]))
    for t in [
        "College project report: docs\\AgriTech final.pdf",
        "Short run notes: RUN_PRESENTATION.md",
        "Image list: DEMO_IMAGES.md and DEMO_TESTED_IMAGES\\README.txt",
    ]:
        story.append(Paragraph(f"• {t}", st["bullet"]))

    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(
        "Checklist before presentation: Backend running · Frontend open · "
        "DEMO_TESTED_IMAGES ready · Browser zoom comfortable for projector.",
        st["warn"],
    ))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("— End of Setup &amp; Demo Guide —", st["fig"]))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    OUT_ROOT.write_bytes(OUT.read_bytes())
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_ROOT}")


if __name__ == "__main__":
    build()
