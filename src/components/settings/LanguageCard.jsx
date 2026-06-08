import Card from "../common/Card";
import CustomSelect from "../common/CustomSelect";

const LANGUAGE_OPTIONS = ["English", "Indonesia"];

function LanguageCard({
  systemLanguage,
  setSystemLanguage,
  generationLanguage,
  setGenerationLanguage,
}) {
  return (
    <Card title="Language">
      <div className="settings-row">
        <span>System Language</span>
        <CustomSelect
          value={systemLanguage}
          options={LANGUAGE_OPTIONS}
          onChange={(e) => setSystemLanguage(e.target.value)}
        />
      </div>

      <div className="settings-row">
        <span>Generation Language</span>
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