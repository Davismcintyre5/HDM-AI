import { Loader2 } from 'lucide-react';

export default function Button({ children, variant = 'primary', size = 'md', loading, className = '', ...props }) {
  const base = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors disabled:opacity-50';
  const variants = {
    primary: 'bg-primary text-black hover:bg-primary-hover',
    secondary: 'bg-bg-tertiary text-text-primary hover:bg-border border border-border',
    danger: 'bg-danger text-white hover:opacity-90',
    ghost: 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary',
  };
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} disabled={loading || props.disabled} {...props}>
      {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
      {children}
    </button>
  );
}