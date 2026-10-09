import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ENDPOINTS } from '../config/api';

const PlantDiseaseDetection = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError('');
  };

  const analyzeImage = async () => {
    if (!selectedImage) return;
    setIsAnalyzing(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedImage);

    try {
      const response = await axios.post(ENDPOINTS.PREDICT_DISEASE, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000,
      });
      const data = response.data;
      if (data.error || data.status === 'invalid_image') {
        setError(data.error || 'Please upload a plant leaf image only.');
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Prediction failed. Is the backend running?');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const confidencePct =
    result?.confidence != null
      ? result.confidence <= 1
        ? (result.confidence * 100).toFixed(1)
        : Number(result.confidence).toFixed(1)
      : null;

  const statusColor =
    result?.status === 'HEALTHY'
      ? 'text-emerald-300'
      : result?.status === 'UNCERTAIN'
        ? 'text-amber-200'
        : 'text-orange-300';

  return (
    <div className="min-h-screen bg-[#152418] pt-24 pb-12 px-6">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => navigate('/')} className="text-white/70 hover:text-[#e8c468] text-sm mb-6">
          ← Back
        </button>

        <h1 className="font-display text-3xl md:text-4xl text-white mb-2">Plant Disease Detection</h1>
        <p className="text-white/60 mb-8">
          Upload a <span className="text-[#e8c468]">plant leaf photo only</span> (close-up). Soil, people, or random photos will be rejected.
        </p>

        <div className="bg-white/[0.04] border border-white/10 rounded-2xl p-6">
          <div className="aspect-square max-h-80 w-full mx-auto mb-6 rounded-xl bg-black/30 overflow-hidden flex items-center justify-center">
            {previewUrl ? (
              <img src={previewUrl} alt="Leaf preview" className="w-full h-full object-contain" />
            ) : (
              <p className="text-white/40 text-sm px-4 text-center">No image selected</p>
            )}
          </div>

          <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 py-3 rounded-lg border border-white/20 text-white hover:bg-white/10"
            >
              Upload leaf image
            </button>
            <button
              type="button"
              onClick={analyzeImage}
              disabled={!selectedImage || isAnalyzing}
              className={`flex-1 py-3 rounded-lg font-semibold ${
                !selectedImage || isAnalyzing
                  ? 'bg-white/10 text-white/40 cursor-not-allowed'
                  : 'bg-[#e8c468] text-[#1a2e1c] hover:bg-[#f0d48a]'
              }`}
            >
              {isAnalyzing ? 'Analyzing…' : 'Analyze'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-6 rounded-xl border border-amber-400/40 bg-amber-500/10 text-amber-100 p-4 text-sm">
            {error}
          </div>
        )}

        {result && !error && (
          <div className="mt-6 rounded-xl border border-white/10 bg-white/[0.04] p-6 text-white space-y-4">
            <h2 className="text-[#e8c468] font-semibold">Result</h2>

            {result.uncertain && (
              <div className="rounded-lg border border-amber-400/30 bg-amber-500/10 text-amber-100 p-3 text-sm">
                {result.message || 'Low confidence — try a clearer leaf photo.'}
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-white/50 text-xs uppercase tracking-wide mb-1">Prediction</p>
                <p className="text-lg font-semibold">{result.class || '—'}</p>
              </div>
              <div>
                <p className="text-white/50 text-xs uppercase tracking-wide mb-1">Confidence</p>
                <p className="text-lg font-semibold">{confidencePct != null ? `${confidencePct}%` : '—'}</p>
              </div>
            </div>

            {result.status && (
              <p className="text-sm">
                Status: <span className={statusColor}>{result.status}</span>
              </p>
            )}

            {result.treatment && (
              <div className="rounded-lg border border-emerald-400/20 bg-emerald-500/5 p-4">
                <p className="text-emerald-300 text-xs uppercase tracking-wide mb-2">How to treat / manage</p>
                <p className="text-sm text-white/85 leading-relaxed">{result.treatment}</p>
              </div>
            )}

            {Array.isArray(result.top_predictions) && result.top_predictions.length > 1 && (
              <div>
                <p className="text-white/50 text-xs uppercase tracking-wide mb-2">Top matches</p>
                <ul className="space-y-2 text-sm">
                  {result.top_predictions.map((item) => {
                    const pct =
                      item.confidence <= 1
                        ? (item.confidence * 100).toFixed(1)
                        : Number(item.confidence).toFixed(1);
                    return (
                      <li key={item.class} className="flex justify-between border border-white/10 rounded-lg px-3 py-2">
                        <span>{item.class}</span>
                        <span className="text-white/60">{pct}%</span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlantDiseaseDetection;
