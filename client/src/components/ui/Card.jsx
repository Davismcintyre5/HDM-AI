export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-bg-secondary border border-border rounded-xl p-6 ${className}`}>
      {children}
    </div>
  );
}