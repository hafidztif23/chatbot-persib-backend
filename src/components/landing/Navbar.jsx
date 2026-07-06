import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom'; 
import Button from '../common/Button';
import { landingData } from '../../data/landingData';
import logoPersib from '../../image/persib-logo2.png';
import '../../styles/landing.css';

const Navbar = () => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <img src={logoPersib} className="nav-logo-img" alt="Persib Logo"/>
        MAUNG BOT
      </div>
      
      <div className={`hamburger ${isMenuOpen ? 'active' : ''}`} onClick={toggleMenu}>
        <span className="bar"></span>
        <span className="bar"></span>
        <span className="bar"></span>
      </div>
      
      <div className={`navbar-menu ${isMenuOpen ? 'active' : ''}`}>
        
        <div className="navbar-links">
          {landingData.navLinks.map((link, index) => (
            <a key={index} href={link.href} onClick={closeMenu}>
              {link.label}
            </a>
          ))}
        </div>
        
        <div className="navbar-actions">
          <Button 
            variant="primary" 
            onClick={() => { 
              closeMenu(); 
              navigate('/login'); 
            }}
          >
            Login
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;