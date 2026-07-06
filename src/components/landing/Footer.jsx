import React from 'react';
import persibLogo from "../../image/persib-logo3.png";
import { landingData } from "../../data/landingData";

const Footer = () => {
  const { footerSocials, footerApps } = landingData;

  return (
    <footer className="footer" id="contact">
      <div className="footer-content">
        
        <div className="footer-col logo-col">
          <img src={persibLogo} alt="Persib Logo" className="footer-logo-img"/>
        </div>

        <div className="vertical-divider"></div>

        <div className="footer-col email-col">
          <span className="col-title">EMAIL</span>
          <a href="mailto:info@persib.co.id" className="email-link">info@persib.co.id</a>
        </div>

        <div className="vertical-divider"></div>

        <div className="footer-col social-col">
          <span className="col-title">MEDIA SOSIAL</span>
          <div className="social-icons">
            {footerSocials.map((link) => (
              <a key={link.label} href={link.href} target="_blank" rel="noopener noreferrer">
                <img src={link.icon} alt={link.label} className="social-icon" />
              </a>
            ))}
          </div>
        </div>

        <div className="vertical-divider"></div>

        <div className="footer-col app-col">
          <span className="col-title">UNDUH APLIKASI</span>
          <div className="app-badges">
            {footerApps.map((app) => (
              <a key={app.label} href={app.href} target="_blank" rel="noopener noreferrer">
                <img src={app.icon} alt={app.label} className="app-badge" />
              </a>
            ))} 
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;