import { useState } from "react";
import { tokenManager, authAPI } from "../../services/api";
import ProfileInfoSection from "./ProfileInfoSection";
import PasswordSection from "./PasswordSection";
import Button from "../common/Button";

function ProfileForm() {
  // Mengambil data dari tokenManager saat pertama kali load
  const [formData, setFormData] = useState(() => {
    const user = tokenManager.getUser();
    return {
      name: user?.nama_lengkap || "",
      email: user?.email || "",
      password: "",
      confirmPassword: ""
    };
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    if (!formData.password?.trim() || !formData.confirmPassword?.trim()) {
      alert("❌ Kolom Password dan Confirm Password wajib diisi!");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      alert("❌ Password dan Confirm Password tidak cocok! Silakan periksa kembali.");
      return;
    }

    try {
      await authAPI.updateProfile({
        nama_lengkap: formData.name,
        email: formData.email,
        password: formData.password
      });

      // Update local storage user info
      const currentUser = tokenManager.getUser() || {};
      const updatedUser = {
        ...currentUser,
        nama_lengkap: formData.name,
        email: formData.email
      };
      tokenManager.setUser(updatedUser);
      
      alert("✨ Profil berhasil diperbarui!");
      window.location.reload();
    } catch (error) {
      console.error(error);
      alert(`❌ Gagal memperbarui profil: ${error.message}`);
    }
  };

  return (
    <div className="profile-card">
      <ProfileInfoSection formData={formData} onChange={handleInputChange} />
      <div className="profile-divider"></div>
      <PasswordSection formData={formData} onChange={handleInputChange} />
      
      <div className="profile-actions">
        <Button className="profile-update-btn" onClick={handleSave}>
          Update →
        </Button>
      </div>
    </div>
  );
}

export default ProfileForm;