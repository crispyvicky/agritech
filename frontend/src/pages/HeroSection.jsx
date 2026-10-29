import React, { useEffect, useState } from 'react';

const HeroSection = () => {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 80);
    return () => clearTimeout(timer);
  }, []);

  const scrollToTools = () => {
    document.getElementById('tools')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen overflow-hidden">
      <div
        className="absolute inset-0 bg-cover bg-center scale-105"
        style={{ backgroundImage: "url('/farm.avif')" }}
      />
      <div className="absolute inset-0 bg-gradient-to-br from-[#0f1f12]/92 via-[#1a2e1c]/75 to-[#0f1f12]/40" />

      <div className="relative z-10 min-h-screen max-w-6xl mx-auto px-6 flex flex-col justify-center pt-24 pb-16">
        <div
          className={`max-w-xl transition-all duration-1000 ${
            isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <p className="font-display text-5xl sm:text-6xl md:text-7xl leading-none text-white mb-3">
            Agri<span className="text-[#e8c468]">Tech</span>
          </p>
          <h1 className="text-xl sm:text-2xl md:text-3xl font-medium text-white/95 mb-4 tracking-tight">
            Detect plant disease &amp; soil type from photos
          </h1>
          <p className="text-base md:text-lg text-white/75 leading-relaxed mb-8 max-w-md">
            Upload a leaf or soil image, or enter field readings for a crop recommendation you can use for the farm.
          </p>
          <button
            onClick={scrollToTools}
            className="bg-[#e8c468] text-[#1a2e1c] font-semibold px-7 py-3.5 rounded-md hover:bg-[#f0d48a] transition-all duration-300 hover:-translate-y-0.5"
          >
            Open tools
          </button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
