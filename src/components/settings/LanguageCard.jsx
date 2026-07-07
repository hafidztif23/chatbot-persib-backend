import Card from "../common/Card";
import CustomSelect from "../common/CustomSelect";
import { useAuth } from "../../hooks/useAuth";
import { getTranslation } from "../../utils/translation";

const LANGUAGE_OPTIONS = ["English", "Indonesia"];

function LanguageCard({
  systemLanguage,
  setSystemLanguage,
  generationLanguage,
  setGenerationLanguage,
}) {
  const { user } = useAuth();
  const t = getTranslation(user?.referensi_bahasa);

  return (
    <Card title={t.card_language}>
      <div className="settings-row">
        <span>{t.system_lang}</span>
        <CustomSelect
          value={systemLanguage}
          options={LANGUAGE_OPTIONS}
          onChange={(e) => setSystemLanguage(e.target.value)}
        />
      </div>

      <div className="settings-row">
        <span>{t.gen_lang}</span>
        <CustomSelect
          value={generationLanguage}
          options={LANGUAGE_OPTIONS}
          onChange={(e) => setGenerationLanguage(e.target.value)}
        />
      </div>
    </Card>
  );
}

export default LanguageCard;