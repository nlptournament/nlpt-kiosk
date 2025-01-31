/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  darkMode: 'media',
  theme: {
    extend: {
        fontFamily: {
            sans: ['Orbitron'],
        },
        fontSize: {
            '1xl': ['1.2vh', '1.9vh'],
            '2xl': ['1.9vh', '2.5vh'],
            '3xl': ['2.4vh', '2.9vh'],
            '4xl': ['2.8vh', '3.2vh'],
            '5xl': ['3.8vh', '3.8vh'],
            '6xl': ['4.8vh', '4.8vh'],
            '7xl': ['5.8vh', '5.7vh'],
            '8xl': ['7.5vh', '7.6vh'],
            '9xl': ['10.1vh', '10.2vh']
        },
        colors: {
            'background': '#000000',
            'card': '#666666',
            'text': '#ffffe1',
            'highlight': '#6ab63c',
            'red': '#ff0000',
            'green': '#00ff00'
        },
    }
  },
  plugins: [],
}

