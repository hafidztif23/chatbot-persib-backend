import React from 'react';
import persibLogo from "../../images/persib-logo.png";
import { landingData } from "../../data/landingData";

const Footer = () => {
  const { footerSocials, footerLinks } = landingData;

  return (
    <footer className="footer" id="contact">
      <div className="footer-content">
        
        <div className="footer-brand">
          <div className="footer-logo">  
            <img src={persibLogo} alt="Persib Logo" className="footer-logo-img"/>
            <span>PERSIB</span>
          </div>
          <p className="social-text">Media Social</p>
          <div className="social-icons">
            {footerSocials.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={link.label}
              >
                <img src={link.icon} alt={link.label} className="social-icon" />
              </a>
            ))}
          </div>
        </div>

        <div className="footer-links-grid">
          {footerLinks.map((column) => (
            <div key={column.title} className="footer-column">
              <h4>{column.title}</h4>
              {column.items.map((link) => (
                <a key={link.label} href={link.href}>
                  {link.label}
                </a>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="footer-bottom">
        <p>© 2026 PT PERSIB Bandung Bermartabat. All rights reserved.</p>
        <p>Designed with Passion for Bobotoh.</p>
      </div>
    </footer>
  );
};

export default Footer;