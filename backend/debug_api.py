#!/usr/bin/env python3
"""
Test script to debug the soil prediction endpoint
"""

import requests
import json
import os
from PIL import Image
import numpy as np

def test_soil_prediction():
    """Test the soil prediction endpoint"""
    
    # Create a simple test image
    test_image = Image.new('RGB', (180, 180), color='brown')
    test_image.save('test_soil.jpg')
    
    # Test the live endpoint
    url = "https://AgriTech-f1ut.onrender.com/predict-soil"
    
    print(f"🧪 Testing soil prediction endpoint: {url}")
    
    try:
        with open('test_soil.jpg', 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Clean up
    if os.path.exists('test_soil.jpg'):
        os.remove('test_soil.jpg')

def test_health_endpoint():
    """Test the health endpoint"""
    url = "https://AgriTech-f1ut.onrender.com/health"
    
    print(f"🏥 Testing health endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 Health status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting AgriTech API diagnostics...")
    
    test_health_endpoint()
    print("\n" + "="*50 + "\n")
    test_soil_prediction()
    
    print("\n🎯 Diagnostics complete!")
