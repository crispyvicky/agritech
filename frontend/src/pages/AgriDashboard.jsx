import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AgriDashboard = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const dashboardCards = [
    {
      id: 1,
      title: 'Plant Disease Detection',
      description: 'Upload a leaf photo. The AI model classifies the plant condition from the image.',
      path: '/disease-detection',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="w-10 h-10">
          <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
      ),
    },
    {
      id: 2,
      title: 'Soil Detection',
      description: 'Upload a soil photo. The system classifies soil type and suggests suitable crops.',
      path: '/SoilPredictor',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="w-10 h-10">
          <path d="M12 3c-4 4-7 7.5-7 11a7 7 0 0014 0c0-3.5-3-7-7-11z" />
          <path d="M12 14v4" />
        </svg>
      ),
    },
    {
      id: 3,
      title: 'Crop Recommendation',
      description: 'Enter soil N-P-K, pH and local climate. The model recommends the best crop to sow.',
      path: '/crop-recommendation',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="w-10 h-10">
          <path d="M12 21V10" />
          <path d="M12 10c0-3.5 2.5-6 6-6 0 3.5-2.5 6-6 6z" />
          <path d="M12 14c0-3-2.2-5-5-5 0 3 2.2 5 5 5z" />
          <path d="M5 21h14" />
        </svg>
      ),
    },
  ];

  return (
    <section id="tools" className="relative w-full min-h-[70vh] bg-[#152418] py-20 px-6 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(232,196,104,0.08),transparent_40%),radial-gradient(circle_at_80%_70%,rgba(80,140,90,0.12),transparent_45%)]" />

      <div className="max-w-5xl mx-auto relative z-10">
        <header
          className={`text-center mb-12 transition-all duration-700 ${
            isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-6'
          }`}
        >
          <p className="text-[#e8c468] uppercase tracking-[0.2em] text-xs font-semibold mb-3">
            AI farming tools
          </p>
          <h2 className="font-display text-white text-4xl md:text-5xl mb-4">Farming tools</h2>
          <p className="text-white/60 max-w-lg mx-auto text-sm md:text-base">
            Upload a photo or enter field readings — get a prediction. No fake stats, no wallet apps.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {dashboardCards.map((card, index) => (
            <button
              key={card.id}
              type="button"
              onClick={() => navigate(card.path)}
              className="group text-left bg-white/[0.04] border border-white/10 rounded-2xl p-8 flex flex-col transition-all duration-300 hover:bg-[#e8c468] hover:border-[#e8c468] hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-[#e8c468]/50"
              style={{
                transitionDelay: `${index * 60}ms`,
                opacity: isLoaded ? 1 : 0,
                transform: isLoaded ? 'translateY(0)' : 'translateY(24px)',
              }}
            >
              <div className="w-14 h-14 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-[#e8c468] group-hover:bg-[#1a2e1c]/15 group-hover:text-[#1a2e1c] transition-colors mb-5">
                {card.icon}
              </div>
              <h3 className="font-semibold text-xl text-white group-hover:text-[#1a2e1c] transition-colors mb-2">
                {card.title}
              </h3>
              <p className="text-sm text-white/55 group-hover:text-[#1a2e1c]/75 leading-relaxed flex-1 transition-colors">
                {card.description}
              </p>
              <div className="mt-6 flex items-center text-sm font-semibold text-[#e8c468] group-hover:text-[#1a2e1c] transition-colors">
                Open
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1 transition-transform group-hover:translate-x-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AgriDashboard;
