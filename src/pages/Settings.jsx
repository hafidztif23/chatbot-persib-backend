import { useState, useEffect } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import LanguageCard from "../components/settings/LanguageCard";
import ThemeCard from "../components/settings/ThemeCard";
import Button from "../components/common/Button";
import { useAuth } from "../hooks/useAuth";
import { authAPI } from "../services/api";
import { getTranslation } from "../utils/translation";
import "../styles/settings.css";

function Settings() {
  const { user, updateUser } = useAuth();
  const t = getTranslation(user?.referensi_bahasa);

  // Baca pengaturan dari user profil database (default: 'ind' -> Indonesia, 'eng' -> English)
  const [systemLanguage, setSystemLanguage] = useState(
    user?.referensi_bahasa === "eng" ? "English" : "Indonesia"
  );

  const [theme, setTheme] = useState(() => 
    localStorage.getItem("settings_theme") ?? "Dark"
  );

  // Update local states jika data user berubah (misal baru login atau data sync)
  useEffect(() => {
    if (user) {
      setSystemLanguage(user.referensi_bahasa === "eng" ? "English" : "Indonesia");
    }
  }, [user]);

  const handleSave = async () => {
    try {
      const ref_bahasa = systemLanguage === "English" ? "eng" : "ind";

      // 1. Simpan ke database backend
      await authAPI.updateProfile({
        referensi_bahasa: ref_bahasa,
      });

      // 2. Sinkronisasi global auth state agar langsung me-render ulang seluruh halaman/Sidebar
      const updatedUser = {
        ...user,
        referensi_bahasa: ref_bahasa,
      };
      updateUser(updatedUser);

      // 3. Simpan setting dummy lokal lainnya (Theme)
      localStorage.setItem("settings_theme", theme);

      alert(t.save_success || "Pengaturan berhasil disimpan!");
    } catch (error) {
      console.error("Gagal menyimpan pengaturan:", error);
      alert("Gagal menyimpan pengaturan: " + (error.message || error));
    }
  };

  return (
    <DashboardLayout>
      <div className="settings-page">
        <h1 className="settings-title">{t.settings_title}</h1>
        
        <div className="settings-grid">
          <LanguageCard 
             systemLanguage={systemLanguage} 
             setSystemLanguage={setSystemLanguage}
          />
          <ThemeCard 
             theme={theme} 
             setTheme={setTheme}
          />
        </div>

        <div className="settings-actions">
          <Button className="profile-update-btn" onClick={handleSave}>
            {t.update_btn}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default Settings;