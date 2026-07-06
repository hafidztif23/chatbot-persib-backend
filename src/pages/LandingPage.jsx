import React from 'react';
import Navbar from '../components/landing/Navbar';
import HeroSection from '../components/landing/HeroSection';
import TestimonialsSection from '../components/landing/TestimonialsSection';
import UseCaseSection from '../components/landing/UseCaseSection';
import FAQSection from '../components/landing/FAQSection';
import Footer from '../components/landing/Footer';
import heroBg2 from "../image/hero-bg2.jpg";
import '../styles/landing.css';

const LandingPage = () => {
  return (
    <div className="landing-page">
      <div className="container">
        <Navbar />
        <HeroSection />
        <div className="landing-grid" style={{backgroundImage: `linear-gradient(rgba(0,20,60,0.75),rgba(0,10,40,0.85)),url(${heroBg2})`}}>
          <div className="grid-full" id="features"><UseCaseSection /></div>     
          <div className="grid-full" id="review"><TestimonialsSection /></div>
          <div className="grid-full" id="faq"><FAQSection /></div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default LandingPage;