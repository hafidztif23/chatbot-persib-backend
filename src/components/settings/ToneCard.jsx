import Card from "../common/Card";
import CustomSelect from "../common/CustomSelect";

const TONE_OPTIONS = ["Formal", "Casual"];

function ToneCard({ tone, setTone, formalityLevel, setFormalityLevel }) {
  return (
    <Card title="Tone">
      <div className="settings-row">
        <span>Tone Style</span>
        <CustomSelect
          value={tone}
          options={TONE_OPTIONS}
          onChange={(e) => setTone(e.target.value)}
        />
      </div>

      <div className="settings-row">
        <span>Formality Level</span>
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