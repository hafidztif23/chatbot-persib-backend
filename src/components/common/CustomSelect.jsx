import "../../styles/components/select.css";

function CustomSelect({
  label,
  value,
  options,
  onChange,
}) {
  return (
    <div className="custom-select">
      {label && (
        <label>
          {label}
        </label>
      )}
      <select value={value} onChange={onChange}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}

export default CustomSelect;