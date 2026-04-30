/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Editorial neutral scale (warm paper tones)
        bg: {
          DEFAULT: '#FBF9F4', // page background
          soft: '#F5F1E8',    // secondary surface
          card: '#FFFFFF',
        },
        ink: {
          900: '#141210',   // primary text
          700: '#2A2622',
          500: '#6B645C',   // secondary text
          300: '#B8AFA3',   // tertiary / hairlines
          200: '#E5DFD3',   // borders
          100: '#EFEAE0',   // subtle fills
        },
        accent: {
          DEFAULT: '#E85D1C', // the single brand orange (paper-orange)
          soft: '#FFE8D5',
          deep: '#B8440E',
        },
      },
      fontFamily: {
        // Editorial display serif with real character
        display: ['"Instrument Serif"', '"Noto Serif SC"', 'Georgia', 'serif'],
        serif: ['"Noto Serif SC"', '"Instrument Serif"', 'Georgia', 'serif'],
        sans: ['"Inter"', '"Noto Sans SC"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        // For huge display typography
        'display-sm': ['clamp(2.5rem, 6vw, 4rem)', { lineHeight: '1', letterSpacing: '-0.02em' }],
        'display-md': ['clamp(3rem, 8vw, 5.5rem)', { lineHeight: '0.95', letterSpacing: '-0.03em' }],
        'display-lg': ['clamp(4rem, 12vw, 9rem)', { lineHeight: '0.9', letterSpacing: '-0.04em' }],
        'display-xl': ['clamp(5rem, 16vw, 14rem)', { lineHeight: '0.85', letterSpacing: '-0.05em' }],
      },
      letterSpacing: {
        tightest: '-0.05em',
      },
      maxWidth: {
        'prose-wide': '72ch',
        'page': '1100px',
      },
      animation: {
        'rise': 'rise 0.9s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'fade': 'fade 1s ease-out forwards',
        'blink': 'blink 1.1s step-end infinite',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fade: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
