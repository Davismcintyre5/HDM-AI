import { forwardRef } from 'react';

const Input = forwardRef(({ label, error, className = '', ...props }, ref) => (
  <div className="w-full">
    {label && <label className="block text-sm text-text-secondary mb-1">{label}</label>}
    <input
      ref={ref}
      className={`w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:border-primary transition-colors ${error ? 'border-danger' : ''} ${className}`}
      {...props}
    />
    {error && <p className="text-danger text-xs mt-1">{error}</p>}
  </div>
));

Input.displayName = 'Input';
export default Input;