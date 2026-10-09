import React, { useEffect, useState } from 'react';
import './App.css';
import Header from './pages/Header';
import HeroSection from './pages/HeroSection';
import Dashboard from './pages/AgriDashboard';
import PlantDiseaseDetection from './pages/PlantDiseaseDetection';
import SoilPredictor from './pages/SoilPredictor';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setLoaded(true);

    const checkVisibility = () => {
      document.querySelectorAll('.scroll-reveal').forEach((section) => {
        if (section.getBoundingClientRect().top < window.innerHeight * 0.9) {
          section.classList.add('visible');
        }
      });
    };

    setTimeout(checkVisibility, 80);
    window.addEventListener('scroll', checkVisibility);
    return () => window.removeEventListener('scroll', checkVisibility);
  }, []);

  return (
    <Router>
      <div className={`App ${loaded ? 'app-loaded' : ''}`}>
        <Header />
        <Routes>
          <Route path="/disease-detection" element={<PlantDiseaseDetection />} />
          <Route path="/SoilPredictor" element={<SoilPredictor />} />
          <Route
            path="/"
            element={
              <div className="content-container">
                <div className="scroll-reveal">
                  <HeroSection />
                </div>
                <div className="scroll-reveal">
                  <Dashboard />
                </div>
                <footer className="bg-[#0f1f12] text-white/40 text-center text-sm py-8 px-4 border-t border-white/5">
                  <span className="font-display text-white/70">AgriTech</span>
                  <span className="mx-2">·</span>
                  Plant disease &amp; soil image AI
                </footer>
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
