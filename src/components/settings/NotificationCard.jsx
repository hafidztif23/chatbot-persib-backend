import Card from "../common/Card";
import ToggleSwitch from "../common/ToggleSwitch";

function NotificationCard({ notifications, setNotifications }) {
  return (
    <Card title="Notifications">
      <div className="settings-row">
        <span className="settings-label">Enable Notifications</span>
        <ToggleSwitch
          checked={notifications}
          onChange={() => setNotifications((prev) => !prev)}
        />
      </div>
    </Card>
  );
}

export default NotificationCard;