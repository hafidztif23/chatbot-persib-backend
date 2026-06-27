import Input from "../common/Input";

function ProfileInfoSection({ formData, onChange }) {
  return (
    <div className="profile-section">
      <h2>Personal Information</h2>
      <div className="profile-grid">
        <Input
          label="Your fullname*"
          name="name" 
          value={formData.name}
          onChange={onChange}
        />
        <Input
          label="Your email*"
          name="email"
          type="email"
          value={formData.email}
          onChange={onChange}
        />
      </div>
    </div>
  );
}

export default ProfileInfoSection;