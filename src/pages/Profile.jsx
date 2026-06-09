import { useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import ProfileTabs from "../components/profile/ProfileTabs";
import ProfileForm from "../components/profile/ProfileForm";
import EmptyTab from "../components/profile/EmptyTab";
import "../styles/profile.css";

function Profile() {
  const [activeTab, setActiveTab] = useState("details");

  return (
    <DashboardLayout>
      <div className="profile-page">
        <ProfileTabs activeTab={activeTab} setActiveTab={setActiveTab} />
        
        {activeTab === "details" ? <ProfileForm /> : <EmptyTab />}
      </div>
    </DashboardLayout>
  );
}

export default Profile;