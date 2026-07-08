import Card from "../common/Card";
import CustomSelect from "../common/CustomSelect";
import { useAuth } from "../../hooks/useAuth";
import { getTranslation } from "../../utils/translation";

const THEME_OPTIONS = ["Dark", "Sun"];

function ThemeCard({ theme, setTheme }) {
  const { user } = useAuth();
  const t = getTranslation(user?.referensi_bahasa);

  return (
    <Card title="Theme">
      <div className="settings-row">
        <span>SELECT THEME</span>
        <CustomSelect
          value={theme}
          options={THEME_OPTIONS}
          onChange={(e) => setTheme(e.target.value)}
        />
      </div>
    </Card>
  );
}

export default ThemeCard;
