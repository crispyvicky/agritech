import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ENDPOINTS } from '../config/api';

function SoilPredictor() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setResult(null);
      setError('');
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please upload a soil image first.');
      return;
    }
    setIsLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(ENDPOINTS.PREDICT_SOIL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000,
      });
      if (res.data?.error || res.data?.status === 'invalid_image') {
        setError(res.data.error || 'Please upload a soil image only.');
        setResult(null);
      } else {
        setResult(res.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Prediction failed. Is the backend running?');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#152418] pt-24 pb-12 px-6">
      <div className="max-w-3xl mx-auto">
        <button onClick={() => navigate('/')} className="text-white/70 hover:text-[#e8c468] text-sm mb-6">
          ← Back
        </button>

        <h1 className="font-display text-3xl md:text-4xl text-white mb-2">Soil Detection</h1>
        <p className="text-white/60 mb-8">
          Upload a <span className="text-[#e8c468]">soil photo only</span> (bare ground close-up). Leaf/plant photos will be rejected.
        </p>

        <div className="bg-white/[0.04] border border-white/10 rounded-2xl p-6">
          <div
            className="border border-dashed border-white/20 rounded-xl p-8 text-center mb-4"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              if (e.dataTransfer.files?.[0]) {
                setFile(e.dataTransfer.files[0]);
                setResult(null);
                setError('');
              }
            }}
          >
            {preview ? (
              <img src={preview} alt="Soil preview" className="max-h-64 mx-auto rounded-lg object-contain" />
            ) : (
              <p className="text-white/40 text-sm">Drag & drop a soil image, or select one</p>
            )}
          </div>

          <input id="soilFile" type="file" accept="image/*" className="hidden" onChange={handleFileChange} />

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              type="button"
              onClick={() => document.getElementById('soilFile')?.click()}
              className="flex-1 py-3 rounded-lg border border-white/20 text-white hover:bg-white/10"
            >
              Select soil image
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!file || isLoading}
              className={`flex-1 py-3 rounded-lg font-semibold ${
                !file || isLoading
                  ? 'bg-white/10 text-white/40 cursor-not-allowed'
                  : 'bg-[#e8c468] text-[#1a2e1c] hover:bg-[#f0d48a]'
              }`}
            >
              {isLoading ? 'Analyzing…' : 'Predict soil type'}
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
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-white/50 text-xs uppercase tracking-wide mb-1">Soil type</p>
                <p className="text-lg font-semibold">{result.prediction}</p>
              </div>
              <div>
                <p className="text-white/50 text-xs uppercase tracking-wide mb-1">Confidence</p>
                <p className="text-lg font-semibold">
                  {typeof result.confidence === 'number' ? `${result.confidence.toFixed(0)}%` : result.confidence}
                </p>
              </div>
            </div>
            {result.notes && <p className="text-sm text-white/70">{result.notes}</p>}
            {(result.grow_tip || result.crops?.length > 0) && (
              <div className="rounded-lg border border-emerald-400/20 bg-emerald-500/5 p-4">
                <p className="text-emerald-300 text-xs uppercase tracking-wide mb-2">What you can grow</p>
                <p className="text-sm text-white/85">
                  {result.grow_tip || `You can typically grow: ${result.crops.join(', ')}.`}
                </p>
              </div>
            )}
            {result.care?.length > 0 && (
              <div>
                <p className="text-white/50 text-xs uppercase tracking-wide mb-2">Care tips</p>
                <ul className="text-sm text-white/80 list-disc pl-5 space-y-1">
                  {result.care.map((tip) => (
                    <li key={tip}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SoilPredictor;
