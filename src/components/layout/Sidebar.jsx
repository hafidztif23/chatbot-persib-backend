import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { getTranslation } from "../../utils/translation";
import "../Chatbot.css";

function Sidebar({ isOpen, setIsOpen }) {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

  const isAdmin = user?.role === 'admin' || user?.email?.endsWith('@persib.co.id') || user?.email?.includes('admin');

  // Ambil kamus terjemahan berdasarkan preferensi user
  const t = getTranslation(user?.referensi_bahasa);

  const handleLogout = () => {
    logout();
  };

  return (
    <aside className={`cb-sidebar sidebar ${isOpen ? 'open' : ''}`}>
      <div className="cb-sidebar-header">
        <div className="cb-bot-icon">🤖</div>
        <div className="cb-bot-title">
          <h3>MAUNG BOT</h3>
          <p>Powered by AI</p>
        </div>
        {/* Close Button for Mobile Sidebar */}
        <button className="cb-close-sidebar-btn" onClick={() => setIsOpen(false)} aria-label="Tutup Menu">
          ✕
        </button>
      </div>

      {!isAdmin && (
        <button className="cb-new-chat-btn" onClick={() => {
          navigate("/chat");
          setIsOpen(false);
        }}>
          <span>➕ {t.new_chat}</span>
        </button>
      )}

      <div className="cb-sidebar-menu">
        <h4>{t.menu_utama}</h4>
        {!isAdmin && (
          <Link to="/chat" className={`cb-menu-item ${currentPath === '/chat' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
            💬 {t.chat_sekarang}
          </Link>
        )}
        {isAdmin && (
          <Link to="/knowledge-base" className={`cb-menu-item ${currentPath === '/knowledge-base' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
            💬 {t.knowledge_base}
          </Link>
        )}
      </div>

      <div className="cb-sidebar-footer">
        <h4>{t.user_menu}</h4>
        <Link to="/profile" className={`cb-menu-item ${currentPath === '/profile' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          👤 {t.edit_profil}
        </Link>
        
        <h4>{t.pengaturan_menu}</h4>
        <Link to="/settings" className={`cb-settings-item ${currentPath === '/settings' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          <span>⚙️ {t.settings}</span>
        </Link>
      </div>

      <button className="cb-logout-btn" onClick={handleLogout}>{t.logout}</button>
    </aside>
  );
}

export default Sidebar;