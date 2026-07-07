import Card from "../common/Card";
import CustomSelect from "../common/CustomSelect";
import { useAuth } from "../../hooks/useAuth";
import { getTranslation } from "../../utils/translation";

const TONE_OPTIONS = ["Formal", "Casual"];

function ToneCard({ tone, setTone, formalityLevel, setFormalityLevel }) {
  const { user } = useAuth();
  const t = getTranslation(user?.referensi_bahasa);

  return (
    <Card title={t.card_tone}>
      <div className="settings-row">
        <span>{t.tone_style}</span>
        <CustomSelect
          value={tone}
          options={TONE_OPTIONS}
          onChange={(e) => setTone(e.target.value)}
        />
      </div>

      <div className="settings-row">
        <span>{t.formality_level}</span>
        <CustomSelect
          value={formalityLevel}
          options={TONE_OPTIONS}
          onChange={(e) => setFormalityLevel(e.target.value)}
        />
      </div>
    </Card>
  );
}

export default ToneCard;