function ProfileTabs({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "details", label: "Profile Details" },
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