import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { tokenManager } from "../../services/api";
import { useAuth } from "../../hooks/useAuth";
import "../Chatbot.css";

function Sidebar({ isOpen, setIsOpen }) {
  const { logout } = useAuth();
  const [user, setUser] = useState(tokenManager.getUser());
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

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

      <button className="cb-new-chat-btn" onClick={() => {
        navigate("/chat");
        setIsOpen(false);
      }}>
        <span>➕ Obrolan Baru</span>
      </button>

      <div className="cb-sidebar-menu">
        <h4>MENU UTAMA</h4>
        <Link to="/chat" className={`cb-menu-item ${currentPath === '/chat' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          💬 Chat Sekarang
        </Link>
        <Link to="/knowledge-base" className={`cb-menu-item ${currentPath === '/knowledge-base' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          💬 Knowledge Base
        </Link>
      </div>

      <div className="cb-sidebar-footer">
        <h4>USER</h4>
        <Link to="/profile" className={`cb-menu-item ${currentPath === '/profile' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          👤 Edit Profil
        </Link>
        
        <h4>PENGATURAN</h4>
        <Link to="/settings" className={`cb-settings-item ${currentPath === '/settings' ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          <span>⚙️ Settings</span>
        </Link>
      </div>

      <button className="cb-logout-btn" onClick={handleLogout}>Keluar</button>
    </aside>
  );
}

export default Sidebar;