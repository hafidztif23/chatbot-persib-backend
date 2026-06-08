import React, { useState, useEffect } from 'react';
import { landingData } from '../../data/landingData';

const TestimonialsSection = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const data = landingData.testimonials;

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((current) => (current + 1) % data.length);
    }, 5000); 
    
    return () => clearInterval(interval);
  }, [data.length]);

  return (
    <section className="testimonials-section">
      <div className="section-header-testimoni">
        <h2 className="section-title">Apa Kata Pengguna?</h2>
        <p className="section-description">Pendapat dan pengalaman pengguna setelah menggunakan Maung Bot.</p>
      </div>

      <div className="testimonials-carousel">
        {data.map((item, index) => {
          let diff = index - activeIndex;
          if (diff < -Math.floor(data.length / 2)) diff += data.length;
          if (diff > Math.floor(data.length / 2)) diff -= data.length;

          let stateClass = 'card-hidden';
          if (diff === 0) stateClass = 'card-active';       
          else if (diff === -1) stateClass = 'card-prev';
          else if (diff === 1) stateClass = 'card-next';

          return (
            <div key={index} className={`testimonial-card ${stateClass}`}>
              <div className="quote-mark">“</div>
              <p className="testimonial-text">{item.text}</p>
              <div className="testimonial-divider"></div>
              <div className="testimonial-footer">
                <div className="user-meta">
                  <div className="avatar-placeholder">{item.name.charAt(0)}</div>
                  <div className="user-info-testimoni">
                    <h4>{item.name}</h4>
                    <span>{item.username}</span>
                  </div>
                </div>
                <div className="rating">★★★★★</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="carousel-dots">
        {data.map((_, index) => (
          <button
            key={index}
            className={`dot ${index === activeIndex ? 'active' : ''}`}
            onClick={() => setActiveIndex(index)}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </section>
  );
};

export default TestimonialsSection;