# AgriTech — run for presentation

Only **2 tools** (image AI): Plant Disease Detection + Soil Detection.

## Terminal 1 — Backend

```powershell
cd C:\Users\hrvph_gg5w5\Desktop\agri\AgriSync\backend
$env:PORT="8000"
$env:PYTHONUTF8="1"
.\.venv\Scripts\python.exe start.py
```

## Terminal 2 — Frontend

```powershell
cd C:\Users\hrvph_gg5w5\Desktop\agri\AgriSync\frontend
npm start
```

Open **http://localhost:3000**

## Demo

1. Open **Plant Disease Detection** → upload a leaf photo → Analyze  
2. Open **Soil Detection** → upload a soil photo → Predict  
