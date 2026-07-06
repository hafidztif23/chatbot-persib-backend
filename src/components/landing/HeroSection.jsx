import React from 'react';
import { useNavigate } from 'react-router-dom';

const HeroSection = () => {
  return (
    // Atribut style dihapus, kita akan atur warnanya murni lewat CSS
    <section id="home" className="hero-section">
      <div className="hero-container">
        <div className="hero-content">
          <h1 className="hero-title">
            Jawaban Cepat untuk Bobotoh,<br />
            Kapan Pun Di Mana Pun.
          </h1>
          <p className="hero-description">
            Tanya apa saja seputar ketersediaan tiket, jadwal laga, hingga info keanggotaan Persib. Maung Bot hadir memberi jawaban akurat dan instan dari sumber resmi.
          </p>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;