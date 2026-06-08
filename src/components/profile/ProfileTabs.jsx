function ProfileTabs({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "details", label: "Profile Details" },
    { id: "preferences", label: "Preferences" },
    { id: "usage", label: "Usage" },
    { id: "billing", label: "Plan & Billing" },
    { id: "team", label: "Team" },
    { id: "integrations", label: "Integrations" },
    { id: "api", label: "API Dashboard" },
  ];

  return (
    <div className="profile-tabs">
      <div className="tabs-container">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default ProfileTabs;