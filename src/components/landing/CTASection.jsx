import React from 'react';
import Button from '../common/Button';

const CTASection = () => {
  return (
    <section className="cta-section">
      <div className="cta-card">
        <h2 className="cta-title">Siap Mencoba<br/>Asisten AI Persib?</h2>
        <p className="cta-description">
          Bergabunglah bersama ribuan Bobotoh yang sudah merasakan kemudahan akses informasi instan. Mulai tanyakan semua hal tentang Persib hari ini.
        </p>
        <Button variant="primary" className="cta-btn">Uji Coba Maung Bot</Button>
      </div>
    </section>
  );
};

export default CTASection;