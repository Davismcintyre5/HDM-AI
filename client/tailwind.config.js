/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: 'var(--accent)',
        'primary-hover': 'var(--accentHover)',
        bg: 'var(--bg)',
        'bg-secondary': 'var(--bgSecondary)',
        'bg-tertiary': 'var(--bgTertiary)',
        'text-primary': 'var(--text)',
        'text-secondary': 'var(--textSecondary)',
        'text-muted': 'var(--textMuted)',
        border: 'var(--border)',
        danger: 'var(--danger)',
        success: 'var(--success)',
      },
    },
  },
  plugins: [],
};