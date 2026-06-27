import { useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import NotificationCard from "../components/settings/NotificationCard";
import LanguageCard from "../components/settings/LanguageCard";
import ToneCard from "../components/settings/ToneCard";
import Button from "../components/common/Button";
import "../styles/settings.css";

const KEYS = {
  NOTIFICATIONS: "settings_notifications",
  SYSTEM_LANG: "settings_systemLanguage",
  GEN_LANG: "settings_generationLanguage",
  TONE: "settings_tone",
  FORMALITY: "settings_formalityLevel",
};

function Settings() {
  const [notifications, setNotifications] = useState(() => 
    JSON.parse(localStorage.getItem(KEYS.NOTIFICATIONS)) ?? true
  );
  const [systemLanguage, setSystemLanguage] = useState(() => 
    localStorage.getItem(KEYS.SYSTEM_LANG) ?? "English"
  );
  const [generationLanguage, setGenerationLanguage] = useState(() => 
    localStorage.getItem(KEYS.GEN_LANG) ?? "English"
  );
  const [tone, setTone] = useState(() => 
    localStorage.getItem(KEYS.TONE) ?? "Formal"
  );
  const [formalityLevel, setFormalityLevel] = useState(() => 
    localStorage.getItem(KEYS.FORMALITY) ?? "Casual"
  );

  const handleSave = () => {
    localStorage.setItem(KEYS.NOTIFICATIONS, JSON.stringify(notifications));
    localStorage.setItem(KEYS.SYSTEM_LANG, systemLanguage);
    localStorage.setItem(KEYS.GEN_LANG, generationLanguage);
    localStorage.setItem(KEYS.TONE, tone);
    localStorage.setItem(KEYS.FORMALITY, formalityLevel);
    
    alert("Pengaturan berhasil disimpan!");
  };

  return (
    <DashboardLayout>
      <div className="settings-page">
        <h1 className="settings-title">Settings</h1>
        
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
            Update →
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default Settings;