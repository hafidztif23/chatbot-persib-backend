import userData from "../../data/userData";

function ProfileAvatar() {
  return (
    <div className="profile-avatar">
      <div className="avatar-wrapper">
        <img
          src={userData.avatar}
          alt={userData.name}
          className="avatar-image"
        />
      <button className="avatar-edit-btn">
        ✎
      </button>
      </div>
    </div>
  );
}

export default ProfileAvatar;