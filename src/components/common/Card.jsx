import "../../styles/components/card.css";

function Card({
  title,
  children,
  className = "",
}) {
  return (
    <div className={`app-card ${className}`}>
      {title && (
        <h2 className="app-card-title">
          {title}
        </h2>
      )}
      {children}
    </div>
  );
}

export default Card;