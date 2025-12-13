/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: "#2563EB",
      },
      boxShadow: {
        card: "0 0 25px rgba(0,0,0,0.4)",
      },
    },
  },
  plugins: [],
};
