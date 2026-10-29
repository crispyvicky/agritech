import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ENDPOINTS } from '../config/api';

const FIELDS = [
  { name: 'N', label: 'Nitrogen (N)', unit: 'kg/ha', min: 0, max: 200, step: 1, placeholder: '90' },
  { name: 'P', label: 'Phosphorus (P)', unit: 'kg/ha', min: 0, max: 200, step: 1, placeholder: '42' },
  { name: 'K', label: 'Potassium (K)', unit: 'kg/ha', min: 0, max: 250, step: 1, placeholder: '43' },
  { name: 'temperature', label: 'Temperature', unit: '°C', min: -10, max: 60, step: 0.1, placeholder: '21' },
  { name: 'humidity', label: 'Humidity', unit: '%', min: 0, max: 100, step: 0.1, placeholder: '82' },
  { name: 'ph', label: 'Soil pH', unit: '', min: 0, max: 14, step: 0.1, placeholder: '6.5' },
  { name: 'rainfall', label: 'Rainfall', unit: 'mm', min: 0, max: 500, step: 0.1, placeholder: '203' },
];

const EMPTY = FIELDS.reduce((acc, f) => ({ ...acc, [f.name]: '' }), {});

function CropRecommendation() {
  const [values, setValues] = useState(EMPTY);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const isComplete = FIELDS.every((f) => values[f.name] !== '');

  const handleChange = (e) => {
    setValues({ ...values, [e.target.name]: e.target.value });
    setResult(null);
    setError('');
  };

  const fillSample = () => {
    setValues(FIELDS.reduce((acc, f) => ({ ...acc, [f.name]: f.placeholder }), {}));
    setResult(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isComplete) {
      setError('Please fill in all seven values.');
      return;
    }
    setIsLoading(true);
    setError('');
    setResult(null);

    const payload = FIELDS.reduce((acc, f) => ({ ...acc, [f.name]: Number(values[f.name]) }), {});

    try {
      const res = await axios.post(ENDPOINTS.PREDICT_CROP, payload, { timeout: 60000 });
      if (res.data?.error) {
        setError(res.data.error);
      } else {
        setResult(res.data);
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        Array.isArray(detail)
          ? 'One or more values are out of range.'
          : err.message || 'Recommendation failed. Is the backend running?'
      );
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

        <h1 className="font-display text-3xl md:text-4xl text-white mb-2">Crop Recommendation</h1>
        <p className="text-white/60 mb-8">
          Enter your <span className="text-[#e8c468]">soil nutrients and local climate</span> to get the most suitable crop.
        </p>

        <form onSubmit={handleSubmit} className="bg-white/[0.04] border border-white/10 rounded-2xl p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            {FIELDS.map((f) => (
              <label key={f.name} className="block">
                <span className="text-white/60 text-xs uppercase tracking-wide">
                  {f.label}
                  {f.unit && <span className="text-white/35 normal-case"> ({f.unit})</span>}
                </span>
                <input
                  type="number"
                  name={f.name}
                  min={f.min}
                  max={f.max}
                  step={f.step}
                  value={values[f.name]}
                  placeholder={f.placeholder}
                  onChange={handleChange}
                  className="mt-1 w-full rounded-lg bg-white/5 border border-white/15 px-3 py-2.5 text-white placeholder-white/25 focus:outline-none focus:border-[#e8c468]"
                />
              </label>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              type="button"
              onClick={fillSample}
              className="flex-1 py-3 rounded-lg border border-white/20 text-white hover:bg-white/10"
            >
              Use sample values
            </button>
            <button
              type="submit"
              disabled={!isComplete || isLoading}
              className={`flex-1 py-3 rounded-lg font-semibold ${
                !isComplete || isLoading
                  ? 'bg-white/10 text-white/40 cursor-not-allowed'
                  : 'bg-[#e8c468] text-[#1a2e1c] hover:bg-[#f0d48a]'
              }`}
            >
              {isLoading ? 'Analyzing…' : 'Recommend crop'}
            </button>
          </div>
        </form>

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
                <p className="text-white/50 text-xs uppercase tracking-wide mb-1">Best crop</p>
                <p className="text-lg font-semibold">{result.crop}</p>
              </div>
              <div>
                <p className="text-white/50 text-xs uppercase tracking-wide mb-1">Confidence</p>
                <p className="text-lg font-semibold">{result.confidence.toFixed(0)}%</p>
              </div>
            </div>
            {result.top3?.length > 1 && (
              <div className="rounded-lg border border-emerald-400/20 bg-emerald-500/5 p-4">
                <p className="text-emerald-300 text-xs uppercase tracking-wide mb-2">Other good options</p>
                <ul className="text-sm text-white/85 space-y-1">
                  {result.top3.slice(1).map((c) => (
                    <li key={c.crop}>
                      {c.crop} <span className="text-white/45">({c.confidence.toFixed(0)}%)</span>
                    </li>
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

export default CropRecommendation;
