/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        lds: {
          navy: '#0f2027',
          blue: '#203a43',
          teal: '#2c5364',
          gold: '#d4af37',
          accent: '#00adb5',
          darkBg: '#0b131e',
          cardBg: '#131e2e'
        }
      }
    },
  },
  plugins: [],
}
