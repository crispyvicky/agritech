"""
AgriTech Backend API
Main FastAPI application
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
from PIL import Image
from fastapi.responses import JSONResponse
import io
import numpy as np
import json
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add scripts directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Global variables for lazy loading
soil_model = None
class_names = None
plantdoc_predict_func = None
price_predict_func = None

app = FastAPI(title="AgriTech API", version="1.0.0")

# ✅ Lazy loading functions
def load_soil_model():
    """Load soil classification model lazily"""
    global soil_model, class_names
    if soil_model is None:
        from tensorflow.keras.models import load_model

        labels_path = os.path.join(os.path.dirname(__file__), "models", "class_names.json")
        candidates = [
            os.path.join(os.path.dirname(__file__), "models", "soil_compat.keras"),
            os.path.join(os.path.dirname(__file__), "models", "soil_classifier.keras"),
            os.path.join(os.path.dirname(__file__), "models", "soil_classifier_fallback.keras"),
        ]

        last_error = None
        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                logger.info(f"Loading soil model from: {path}")
                soil_model = load_model(path, compile=False)
                logger.info(f"Soil model loaded: {os.path.basename(path)}")
                break
            except Exception as e:
                logger.warning(f"Soil model failed ({os.path.basename(path)}): {e}")
                last_error = e

        if soil_model is None:
            raise last_error or FileNotFoundError("No soil model available")

        with open(labels_path, "r", encoding="utf-8") as f:
            class_names = json.load(f)
        logger.info(f"Loaded soil classes: {class_names}")

    return soil_model, class_names

def load_plantdoc_predictor():
    """Load plant disease predictor lazily"""
    global plantdoc_predict_func
    if plantdoc_predict_func is None:
        try:
            from predict_plantdoc import predict_disease
            plantdoc_predict_func = predict_disease
            logger.info("Loaded plant disease predictor")
        except Exception as e:
            logger.error(f"Failed to load plant disease predictor: {str(e)}")
            raise e
    
    return plantdoc_predict_func

def load_price_predictor():
    """Load price predictor lazily"""
    global price_predict_func
    if price_predict_func is None:
        try:
            from predict_with_graph import get_price_predictions
            price_predict_func = get_price_predictions
            logger.info("Loaded price predictor")
        except Exception as e:
            logger.error(f"Failed to load price predictor: {str(e)}")
            raise e
    
    return price_predict_func

# ✅ CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://superb-patience-production.up.railway.app",  # Your deployed frontend
        "http://localhost:5173",  # For local development
        "http://localhost:3000",   # Alternative local dev port
        "*"  # For testing - remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount graph images folder
GRAPH_DIR = os.path.join(os.path.dirname(__file__), "scripts", "predicted_graphs")
os.makedirs(GRAPH_DIR, exist_ok=True)
app.mount("/graphs", StaticFiles(directory=GRAPH_DIR), name="graphs")

# ✅ Root endpoint
@app.get("/")
def root():
    return {"message": "AgriTech API is running", "status": "healthy", "version": "1.0.0"}

# ✅ Health check routes
@app.get("/health")
def health_check():
    return {"status": "API is running"}

@app.get("/healthz")
def health_check_detailed():
    """Detailed health check with model status"""
    status = {
        "status": "healthy",
        "message": "AgriTech API is running",
        "version": "1.0.0",
        "models": {
            "soil_model": soil_model is not None,
            "plantdoc_predictor": plantdoc_predict_func is not None,
            "price_predictor": price_predict_func is not None
        }
    }
    return status

# ✅ Plant Disease Prediction
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Load predictor on first use
        predict_func = load_plantdoc_predictor()
        
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = predict_func(file_path)
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return result
    except Exception as e:
        logger.error(f"Plant disease prediction error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Plant disease prediction failed: {str(e)}",
            "prediction": "Unable to predict",
            "confidence": 0.0
        }

# ✅ Market Price Prediction
@app.get("/market-predictions")
def get_predictions_for_graph():
    try:
        # Load predictor on first use
        predict_func = load_price_predictor()
        results = predict_func()
        return {"status": "success", "data": results}
    except Exception as e:
        logger.error(f"Market prediction error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error", 
            "message": f"Market prediction failed: {str(e)}",
            "data": []
        }

# ✅ Soil Type Prediction
IMG_SIZE = (180, 180)


def _looks_like_plant_not_soil(rgb_array: np.ndarray) -> bool:
    """Heuristic: lots of green / little brown-earth tones => not a soil photo."""
    arr = rgb_array.astype("float32")
    if arr.ndim != 3 or arr.shape[2] < 3:
        return False
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    green_dom = (g > r + 15) & (g > b + 15) & (g > 60)
    green_ratio = float(np.mean(green_dom))
    # Earth tones: brown/orange-ish (r and mid g, lower b)
    earth = (r > 40) & (r > b) & (np.abs(r - g) < 80) & (g > 20)
    earth_ratio = float(np.mean(earth))
    return green_ratio > 0.28 and earth_ratio < 0.35


soil_info = {
    "Alluvial soil": {
        "notes": "Fertile soil formed by river deposits, excellent for agriculture.",
        "crops": ["Rice", "Wheat", "Corn", "Sugarcane", "Cotton"],
        "care": ["Ensure proper drainage", "Regular organic matter addition", "Monitor pH levels"]
    },
    "Black Soil": {
        "notes": "Rich in clay and organic matter, retains moisture well.",
        "crops": ["Cotton", "Wheat", "Jowar", "Linseed", "Tobacco"],
        "care": ["Improve drainage", "Add organic compost", "Deep plowing recommended"]
    },
    "Clay soil": {
        "notes": "Dense soil with high water retention, can be challenging for some crops.",
        "crops": ["Rice", "Wheat", "Barley", "Oats"],
        "care": ["Improve drainage", "Add organic matter", "Avoid working when wet"]
    },
    "Red soil": {
        "notes": "Iron-rich soil, generally well-drained but may need nutrient supplementation.",
        "crops": ["Millet", "Groundnut", "Potato", "Tobacco", "Pulses"],
        "care": ["Add lime if acidic", "Regular fertilization", "Organic matter addition"]
    }
}

@app.post("/predict-soil")
async def predict_soil(file: UploadFile = File(...)):
    try:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"soil_{uuid.uuid4().hex}_{file.filename or 'upload.jpg'}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            from predict_soil_embed import predict_soil_from_path

            return predict_soil_from_path(file_path)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        logger.error(f"Soil prediction error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": "Unable to process the image. Please try a clearer soil photo.",
            "prediction": None,
            "confidence": 0.0,
            "crops": [],
            "care": [],
            "status": "error",
        }

# ✅ Print all registered routes on startup
@app.on_event("startup")
async def startup_event():
    logger.info("\n📋 AgriTech API Starting...")
    logger.info("📋 Registered Routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            logger.info(f"➡️  {route.path}")
    
    # Try to load models on startup (optional - will load on first use if this fails)
    try:
        logger.info("🔄 Attempting to pre-load models...")
        
        # Try to load soil model
        try:
            load_soil_model()
            logger.info("✅ Soil model loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Could not pre-load soil model: {e}")
        
        # Try to load plant disease predictor
        try:
            load_plantdoc_predictor()
            logger.info("✅ Plant disease predictor loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Could not pre-load plant disease predictor: {e}")
        
        # Try to load price predictor
        try:
            load_price_predictor()
            logger.info("✅ Price predictor loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Could not pre-load price predictor: {e}")
            
    except Exception as e:
        logger.warning(f"⚠️ Model pre-loading failed: {e}")
        logger.info("📝 Models will be loaded on first use")
    
    logger.info("✅ AgriTech API is ready!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
