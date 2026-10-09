# Demo images (tested — use these)

**Easy folder (copies for demo):**  
`C:\Users\hrvph_gg5w5\Desktop\agri\AgriSync\DEMO_TESTED_IMAGES`

- Plant: `DEMO_TESTED_IMAGES\plant_disease\`
- Soil: `DEMO_TESTED_IMAGES\soil\`

See `DEMO_TESTED_IMAGES\README.txt` for expected labels.

---

## PDFs

| Document | Path |
|----------|------|
| College project report (like `backshot final.pdf`) | `docs\AgriTech final.pdf` |
| Beginner: clone / install / run / present | `docs\AgriTech_Setup_and_Demo_Guide.pdf` |

**Clone:** `git clone https://github.com/crispyvicky/agritech.git`

Also copied to project root with the same filenames.

Regenerate:
```powershell
.\backend\.venv\Scripts\python.exe docs\generate_project_pdf.py
.\backend\.venv\Scripts\python.exe docs\generate_setup_guide_pdf.py
```

---

## Plant Disease (accurate in our tests)

1. **Tomato late blight (DISEASED + treatment tip)**  
   `DEMO_TESTED_IMAGES\plant_disease\01_tomato_late_blight.jpg`

2. **Apple leaf (HEALTHY)**  
   `DEMO_TESTED_IMAGES\plant_disease\02_apple_leaf_healthy.jpg`

3. **Corn rust leaf (DISEASED)**  
   `DEMO_TESTED_IMAGES\plant_disease\03_corn_rust_leaf.jpg`

## Soil (accurate in our tests)

1. **Alluvial soil** — `soil\01_alluvial_soil.jpg`, `soil\02_alluvial_soil.jpg`
2. **Black Soil** — `soil\03_black_soil.jpg`, `soil\04_black_soil.jpg`
3. **Clay soil** — `soil\05_clay_soil.jpg`
4. **Red soil** — `soil\06_red_soil.jpg`

## Wrong-image demo (optional)

- Put a **soil** photo into Plant Disease → should say upload plant leaf only  
- Put a **leaf** photo into Soil → should say upload soil only  
