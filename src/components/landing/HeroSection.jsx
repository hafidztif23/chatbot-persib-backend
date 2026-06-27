import React from 'react';
import Button from '../common/Button';
import heroBg from "../../image/hero-bg.jpg";

const HeroSection = () => {
  return (
    <section className="hero-section" style={{ backgroundImage: `linear-gradient(rgba(0,20,60,0.75),rgba(0,10,40,0.85)),url(${heroBg})` }}>
      <div className="hero-container">
        <div className="hero-content">
          <h1 className="hero-title">
            Jawaban Cepat untuk Bobotoh, Kapan Pun Di Mana Pun.
          </h1>
          <p className="hero-description">
            Tanya apa saja seputar ketersediaan tiket, jadwal laga, hingga info keanggotaan Persib. Maung Bot hadir memberi jawaban akurat dan instan dari sumber resmi.
          </p>
          <div className="hero-buttons">
            <Button variant="primary">Uji Coba Maung Bot</Button>
            <Button variant="outline">Pelajari Cara Kerjanya &rarr;</Button>
          </div>
        </div>
        
        <div className="hero-mockup">
          <div className="chat-window">
            <div className="chat-header">
              <span className="bot-avatar">🤖</span>
              <div className="bot-info">
                <h4>MAUNG BOT</h4>
                <p><span className="status-dot"></span> Online</p>
              </div>
            </div>
            <div className="chat-body">
              <div className="message user-message">
                <p>Kapan pertandingan Persib berikutnya?</p>
              </div>
              <div className="message bot-message">
                <p>Persib Bandung akan menghadapi Bali United pada hari Sabtu, 15 Juni pukul 16:00 WIB di Stadion Gelora Bandung Lautan Api.</p>
              </div>
              <div className="message bot-typing">
                <div className="typing-dots">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
            <div className="chat-input-area">
              <input type="text" placeholder="Tanya Legenda..." readOnly />
              <button className="send-btn">➤</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;