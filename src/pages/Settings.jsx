import { useState, useEffect } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import NotificationCard from "../components/settings/NotificationCard";
import LanguageCard from "../components/settings/LanguageCard";
import ToneCard from "../components/settings/ToneCard";
import Button from "../components/common/Button";
import { useAuth } from "../hooks/useAuth";
import { authAPI } from "../services/api";
import { getTranslation } from "../utils/translation";
import "../styles/settings.css";

function Settings() {
  const { user, updateUser } = useAuth();
  const t = getTranslation(user?.referensi_bahasa);

  const [notifications, setNotifications] = useState(() => 
    JSON.parse(localStorage.getItem("settings_notifications")) ?? true
  );
  
  // Baca pengaturan dari user profil database (default: 1 -> Indonesia, 2 -> English)
  const [systemLanguage, setSystemLanguage] = useState(
    user?.referensi_bahasa === 2 ? "English" : "Indonesia"
  );
  const [generationLanguage, setGenerationLanguage] = useState(
    user?.referensi_generate === 2 ? "English" : "Indonesia"
  );

  const [tone, setTone] = useState(() => 
    localStorage.getItem("settings_tone") ?? "Formal"
  );
  const [formalityLevel, setFormalityLevel] = useState(() => 
    localStorage.getItem("settings_formalityLevel") ?? "Casual"
  );

  // Update local states jika data user berubah (misal baru login atau data sync)
  useEffect(() => {
    if (user) {
      setSystemLanguage(user.referensi_bahasa === 2 ? "English" : "Indonesia");
      setGenerationLanguage(user.referensi_generate === 2 ? "English" : "Indonesia");
    }
  }, [user]);

  const handleSave = async () => {
    try {
      const ref_bahasa = systemLanguage === "English" ? 2 : 1;
      const ref_generate = generationLanguage === "English" ? 2 : 1;

      // 1. Simpan ke database backend
      await authAPI.updateProfile({
        referensi_bahasa: ref_bahasa,
        referensi_generate: ref_generate,
      });

      // 2. Sinkronisasi global auth state agar langsung me-render ulang seluruh halaman/Sidebar
      const updatedUser = {
        ...user,
        referensi_bahasa: ref_bahasa,
        referensi_generate: ref_generate,
      };
      updateUser(updatedUser);

      // 3. Simpan setting dummy lokal lainnya
      localStorage.setItem("settings_notifications", JSON.stringify(notifications));
      localStorage.setItem("settings_tone", tone);
      localStorage.setItem("settings_formalityLevel", formalityLevel);

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
          <NotificationCard 
            notifications={notifications} 
            setNotifications={setNotifications} 
          />
          <LanguageCard 
            systemLanguage={systemLanguage} 
            setSystemLanguage={setSystemLanguage}
            generationLanguage={generationLanguage} 
            setGenerationLanguage={setGenerationLanguage} 
          />
          <ToneCard 
            tone={tone} 
            setTone={setTone}
            formalityLevel={formalityLevel} 
            setFormalityLevel={setFormalityLevel} 
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