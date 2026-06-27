import React, { useState, useEffect } from "react";
import { landingData } from "../../data/landingData";

const UseCaseSection = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const data = landingData.useCases;

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((current) => (current + 1) % data.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [data.length]);

  return (
    <section className="use-case-section">
      <div className="section-header-useCase">
        <h2 className="section-title">Tanya Seputar Persib</h2>
        <p className="section-description">Ketahui informasi apa saja yang bisa kamu tanyakan ke Maung Bot</p>
      </div>

      <div className="carousel-dots">
        {data.map((_, index) => (
          <button
            key={index}
            className={`dot ${index === activeIndex ? "active" : ""}`}
            onClick={() => setActiveIndex(index)}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>

      <div className="use-case-carousel">
        {data.map((useCase, index) => {
          let diff = index - activeIndex;
          if (diff < -Math.floor(data.length / 2)) diff += data.length;
          if (diff > Math.floor(data.length / 2)) diff -= data.length;

          let stateClass = "use-card-hidden";
          if (diff === 0) stateClass = "use-card-active";
          else if (diff === -1) stateClass = "use-card-prev-1";
          else if (diff === 1) stateClass = "use-card-next-1";
          else if (diff === -2) stateClass = "use-card-prev-2";
          else if (diff === 2) stateClass = "use-card-next-2";

          const displayDesc = useCase.desc.length < 20 
            ? `Dapatkan info terbaru terkait ${useCase.title.toLowerCase()} secara instan hanya dengan bertanya ke bot.` 
            : useCase.desc;

          return (
            <div key={index} className={`use-case-card ${stateClass}`}>
              <div className="use-case-image-wrapper">
                <img
                  src={useCase.image}
                  alt={useCase.title}
                  className="use-case-image"
                />
              </div>
              
              <div className="use-case-content">
                <h4 className="use-case-title">{useCase.title}</h4>
                <p className="use-case-desc">{displayDesc}</p>
                <button className="use-case-btn">Tanya Info Ini</button>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default UseCaseSection;