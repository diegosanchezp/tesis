module.exports = {
  // If any css in js has to be added, use
  // "./static/src/**/*.js"
  content: [
    "./templates/**/*.html",
    // Include Flowbite
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        "ucv-yellow": "#FFF9DD"
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('flowbite/plugin'),
  ],
}
