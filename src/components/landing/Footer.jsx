import React from 'react';
import persibLogo from "../../image/persib-logo3.png";
import appStoreBadge from "../../image/app-store.png"; 
import googlePlayBadge from "../../image/google-play.png"; 
import { landingData } from "../../data/landingData";

const Footer = () => {
  const { footerSocials } = landingData;

  return (
    <footer className="footer" id="contact">
      <div className="footer-content">
        
        {/* BLOK 1: Logo */}
        <div className="footer-col logo-col">
          <img src={persibLogo} alt="Persib Logo" className="footer-logo-img"/>
        </div>

        {/* GARIS PEMISAH */}
        <div className="vertical-divider"></div>

        {/* BLOK 2: Email */}
        <div className="footer-col email-col">
          <span className="col-title">EMAIL</span>
          <a href="mailto:info@persib.co.id" className="email-link">info@persib.co.id</a>
        </div>

        {/* GARIS PEMISAH */}
        <div className="vertical-divider"></div>

        {/* BLOK 3: Media Sosial */}
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

        {/* GARIS PEMISAH */}
        <div className="vertical-divider"></div>

        {/* BLOK 4: Unduh Aplikasi */}
        <div className="footer-col app-col">
          <span className="col-title">UNDUH APLIKASI</span>
          <div className="app-badges">
            <a href="#" target="_blank" rel="noopener noreferrer">
              <img src={appStoreBadge} alt="App Store" className="app-badge" />
            </a>
            <a href="#" target="_blank" rel="noopener noreferrer">
              <img src={googlePlayBadge} alt="Google Play" className="app-badge" />
            </a>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;