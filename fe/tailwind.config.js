/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/renderer/**/*.{js,jsx,ts,tsx}', './index.html'],
  theme: {
    extend: {
      fontFamily: {
        aldrich: ['Aldrich', 'sans-serif'],
        roboto: ['Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      },
      width: {
        '628': '628px',
      },
      height: {
        '208': '208px',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
      animation: {
        blink: 'blink 1.4s infinite',
      },
    },
  },
  plugins: [],
}
