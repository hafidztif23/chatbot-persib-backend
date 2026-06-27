import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import "../../styles/components/input.css";

function Input({ label, type = "text", value, onChange, name, placeholder }) {
  const [showPassword, setShowPassword] = useState(false);
  const inputType = type === "password" && showPassword ? "text" : type;

  return (
    <div className="form-group">
      {label && <label>{label}</label>}
      <div className="input-wrapper">
        <input
          type={inputType}
          name={name} 
          value={value}
          onChange={onChange}
          placeholder={placeholder}
        />
        {type === "password" && (
          <button type="button" className="toggle-password" onClick={() => setShowPassword(!showPassword)} >
            {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
          </button>
        )}
      </div>
    </div>
  );
}

export default Input;