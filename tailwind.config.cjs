module.exports = {
  // If any css in js has to be added, use
  // "./static/src/**/*.js"
  content: [
    "./templates/**/*.html",
    // Include Flowbite
    "./node_modules/flowbite/**/*.js",
    "./static/src/js/**/*.ts",
  ],
  theme: {
    extend: {
      colors: {
        "ucv-yellow": {
          DEFAULT: "#FFF9DD",
          dark: "#FFB703",
        },
        "ucv-blue": "#006090",
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('flowbite/plugin'),
  ],
}
