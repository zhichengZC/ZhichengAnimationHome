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
          800: '#8A4010',
        },
        ink: {
          50: '#FAF7F2',
          100: '#E8E2D8',
          300: '#A89D8D',
          500: '#6B6055',
          700: '#3D342A',
          900: '#1F1A14',
        },
        leaf: {
          300: '#A8D89D',
          500: '#6FB564',
          700: '#4A8A3F',
        },
      },
      fontFamily: {
        sans: ['"Noto Sans SC"', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['"Noto Serif SC"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        hand: ['"Caveat"', '"Noto Serif SC"', 'cursive'],
      },
      boxShadow: {
        'soft': '0 4px 20px rgba(229, 122, 44, 0.08)',
        'soft-lg': '0 12px 40px rgba(229, 122, 44, 0.15)',
        'glow': '0 0 24px rgba(255, 154, 77, 0.35)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
        'fade-in': 'fadeIn 1s ease-out forwards',
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 9s ease-in-out infinite',
        'blink': 'blink 1s step-end infinite',
        'gradient': 'gradient 8s ease infinite',
        'tilt': 'tilt 7s ease-in-out infinite',
        'bounce-soft': 'bounceSoft 2.5s ease-in-out infinite',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
        'wave': 'wave 2.5s ease-in-out infinite',
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
        tilt: {
          '0%, 100%': { transform: 'rotate(-2deg)' },
          '50%': { transform: 'rotate(2deg)' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0) scale(1)' },
          '50%': { transform: 'translateY(-6px) scale(1.03)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(255, 154, 77, 0.4)' },
          '50%': { boxShadow: '0 0 24px 6px rgba(255, 154, 77, 0.25)' },
        },
        wave: {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '15%': { transform: 'rotate(14deg)' },
          '30%': { transform: 'rotate(-8deg)' },
          '45%': { transform: 'rotate(14deg)' },
          '60%': { transform: 'rotate(-4deg)' },
          '75%': { transform: 'rotate(10deg)' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
