import Input from "../common/Input";

function PasswordSection({ formData, onChange }) {
  return (
    <div className="profile-section">
      <h2>Password</h2>
      <div className="profile-grid">
        <Input
          label="Password*"
          name="password"
          type="password"
          value={formData.password || ""}
          onChange={onChange}
          placeholder="Masukkan password baru" 
        />
        <Input
          label="Confirm Password*"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword || ""} 
          onChange={onChange}
          placeholder="Konfirmasi password baru" 
        />
      </div>
    </div>
  );
}

export default PasswordSection;