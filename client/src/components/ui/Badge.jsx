export default function Badge({ children, variant = 'primary' }) {
  const variants = {
    primary: 'bg-primary/20 text-primary',
    success: 'bg-success/20 text-success',
    danger: 'bg-danger/20 text-danger',
    info: 'bg-blue-500/20 text-blue-400',
    muted: 'bg-bg-tertiary text-text-muted',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${variants[variant]}`}>
      {children}
    </span>
  );
}