import Card from "../common/Card";
import ToggleSwitch from "../common/ToggleSwitch";
import { useAuth } from "../../hooks/useAuth";
import { getTranslation } from "../../utils/translation";

function NotificationCard({ notifications, setNotifications }) {
  const { user } = useAuth();
  const t = getTranslation(user?.referensi_bahasa);

  return (
    <Card title={t.card_notifications}>
      <div className="settings-row">
        <span className="settings-label">{t.enable_notifications}</span>
        <ToggleSwitch
          checked={notifications}
          onChange={() => setNotifications((prev) => !prev)}
        />
      </div>
    </Card>
  );
}

export default NotificationCard;