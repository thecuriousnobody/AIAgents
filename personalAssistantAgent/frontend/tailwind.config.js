/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f4ff',
          500: '#667eea',
          600: '#5a67d8',
          700: '#4c51bf',
        },
        secondary: {
          500: '#764ba2',
        }
      },
      animation: {
        'pulse-soft': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-subtle': 'bounce 1s ease-in-out infinite',
      }
    },
  },
  plugins: [],
}
