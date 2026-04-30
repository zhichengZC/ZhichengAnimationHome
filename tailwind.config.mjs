/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Warm orange-cream palette (paper-orange theme)
        paper: {
          50: '#FFFBF5',
          100: '#FFF3E4',
          200: '#FFE4C4',
          300: '#FFD39B',
          400: '#FFB86F',
          500: '#FF9A4D',
          600: '#E57A2C',
          700: '#B85A1A',
        },
        ink: {
          50: '#FAF7F2',
          100: '#E8E2D8',
          300: '#A89D8D',
          500: '#6B6055',
          700: '#3D342A',
          900: '#1F1A14',
        },
      },
      fontFamily: {
        sans: ['"Noto Sans SC"', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['"Noto Serif SC"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
        'fade-in': 'fadeIn 1s ease-out forwards',
        'float': 'float 6s ease-in-out infinite',
        'blink': 'blink 1s step-end infinite',
        'gradient': 'gradient 8s ease infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
