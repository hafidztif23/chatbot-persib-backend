import React, { useState } from 'react';
import { landingData } from '../../data/landingData';

const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState(1);

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="faq-section">
      <h2 className="section-title">FAQ</h2>
      <p className="section-description">Accords with real supporter:</p>
      
      <div className="accordion">
        {landingData.faqs.map((faq, index) => (
          <div key={index} className={`accordion-item ${openIndex === index ? 'active' : ''}`}>
            <button className="accordion-header" onClick={() => toggleFAQ(index)}>
              {faq.question}
              <span className="accordion-icon">{openIndex === index ? '^' : 'v'}</span>
            </button>
            {openIndex === index && (
              <div className="accordion-body">
                <p>{faq.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export default FAQSection;