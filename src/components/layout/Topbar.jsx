import { Link } from "react-router-dom";
import profileImage from "../../image/fotoDefault.jpg";
import userData from "../../data/userData";
import "../../styles/topbar.css";

function Topbar({ toggleSidebar }) {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="hamburger-btn" onClick={toggleSidebar}>
          ☰
        </button>
      </div>

      <div className="topbar-right">
        <button className="topbar-icon">💬</button>
        <button className="topbar-icon">🛡️</button>
      </div>
    </header>
  );
}

export default Topbar;