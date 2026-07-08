import Card from "../common/Card";
import CustomSelect from "../common/CustomSelect";
import { useAuth } from "../../hooks/useAuth";
import { getTranslation } from "../../utils/translation";

const SYSTEM_LANGUAGE_OPTIONS = ["English", "Indonesia"];

function LanguageCard({
  systemLanguage,
  setSystemLanguage,
  generationLanguage,
  setGenerationLanguage,
}) {
  const { user } = useAuth();
  const t = getTranslation(user?.referensi_bahasa);

  const genOptions = [
    { value: "English", label: "English" },
    { value: "Otomatis", label: t.gen_lang_otomatis || "Otomatis (Indo/English/Sunda)" }
  ];

  return (
    <Card title={t.card_language}>
      <div className="settings-row">
        <span>{t.system_lang}</span>
        <CustomSelect
          value={systemLanguage}
          options={SYSTEM_LANGUAGE_OPTIONS}
          onChange={(e) => setSystemLanguage(e.target.value)}
        />
      </div>

      <div className="settings-row">
        <span>{t.gen_lang}</span>
        <div className="custom-select">
          <select
            value={generationLanguage}
            onChange={(e) => setGenerationLanguage(e.target.value)}
          >
            {genOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </Card>
  );
}

export default LanguageCard;