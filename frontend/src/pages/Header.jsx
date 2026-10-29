import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const isHome = location.pathname === '/';

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  const handleToolsClick = (e) => {
    if (isHome) {
      e.preventDefault();
      document.getElementById('tools')?.scrollIntoView({ behavior: 'smooth' });
      setMenuOpen(false);
    }
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-400 ${
        scrolled || !isHome
          ? 'bg-[#1a2e1c]/95 backdrop-blur-md shadow-lg py-3'
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
        <Link to="/" className="flex items-baseline no-underline">
          <span className="font-display text-2xl md:text-3xl tracking-tight text-white">Agri</span>
          <span className="font-display text-2xl md:text-3xl tracking-tight text-[#e8c468]">Tech</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          <Link to="/" className="text-sm font-medium text-white/85 hover:text-[#e8c468] no-underline">
            Home
          </Link>
          <a href="/#tools" onClick={handleToolsClick} className="text-sm font-medium text-white/85 hover:text-[#e8c468] no-underline">
            Tools
          </a>
          <Link to="/crop-recommendation" className="text-sm font-medium text-white/85 hover:text-[#e8c468] no-underline">
            Crop Advisor
          </Link>
          {!isHome && (
            <Link
              to="/"
              className="text-sm font-semibold px-4 py-2 rounded-md bg-[#e8c468] text-[#1a2e1c] no-underline"
            >
              Back to Home
            </Link>
          )}
        </nav>

        <button className="md:hidden p-2 text-white" onClick={() => setMenuOpen(!menuOpen)} aria-label="Menu">
          Menu
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden bg-[#1a2e1c] px-6 py-4 flex flex-col gap-3">
          <Link to="/" className="text-white no-underline" onClick={() => setMenuOpen(false)}>Home</Link>
          <a href="/#tools" onClick={handleToolsClick} className="text-white no-underline">Tools</a>
          <Link to="/crop-recommendation" className="text-white no-underline">Crop Advisor</Link>
        </div>
      )}
    </header>
  );
};

export default Header;
