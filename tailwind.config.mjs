/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // All colors driven by CSS variables so light/dark can swap seamlessly
        bg: {
          DEFAULT: 'rgb(var(--bg) / <alpha-value>)',
          soft:    'rgb(var(--bg-soft) / <alpha-value>)',
          card:    'rgb(var(--bg-card) / <alpha-value>)',
          glass:   'rgb(var(--bg-glass) / <alpha-value>)',
        },
        ink: {
          900: 'rgb(var(--ink-900) / <alpha-value>)',
          700: 'rgb(var(--ink-700) / <alpha-value>)',
          500: 'rgb(var(--ink-500) / <alpha-value>)',
          300: 'rgb(var(--ink-300) / <alpha-value>)',
          200: 'rgb(var(--ink-200) / <alpha-value>)',
          100: 'rgb(var(--ink-100) / <alpha-value>)',
        },
        accent: {
          DEFAULT: 'rgb(var(--accent) / <alpha-value>)',
          soft:    'rgb(var(--accent-soft) / <alpha-value>)',
          deep:    'rgb(var(--accent-deep) / <alpha-value>)',
          glow:    'rgb(var(--accent-glow) / <alpha-value>)',
        },
        // A secondary jade / leaf accent for cozy variation
        jade: {
          DEFAULT: 'rgb(var(--jade) / <alpha-value>)',
          soft:    'rgb(var(--jade-soft) / <alpha-value>)',
        },
      },
      fontFamily: {
        display: ['"Fraunces"', '"Noto Serif SC"', 'Georgia', 'serif'],
        serif:   ['"Noto Serif SC"', '"Fraunces"', 'Georgia', 'serif'],
        italic:  ['"Instrument Serif"', '"Fraunces"', 'serif'],
        sans:    ['"Inter"', '"Noto Sans SC"', 'system-ui', '-apple-system', 'sans-serif'],
        mono:    ['"JetBrains Mono"', '"IBM Plex Mono"', 'ui-monospace', 'monospace'],
        hand:    ['"Caveat"', '"Noto Serif SC"', 'cursive'],
      },
      fontSize: {
        'display-sm': ['clamp(2.25rem, 5vw, 3.25rem)', { lineHeight: '1', letterSpacing: '-0.02em' }],
        'display-md': ['clamp(2.75rem, 7vw, 4.75rem)', { lineHeight: '1', letterSpacing: '-0.03em' }],
        'display-lg': ['clamp(3.5rem, 10vw, 7rem)',   { lineHeight: '0.95', letterSpacing: '-0.035em' }],
        'display-xl': ['clamp(4rem, 13vw, 10rem)',    { lineHeight: '0.9', letterSpacing: '-0.04em' }],
      },
      letterSpacing: {
        tightest: '-0.05em',
      },
      maxWidth: {
        'prose-wide': '72ch',
        'page':       '1440px',
        'page-sm':    '1080px',
      },
      boxShadow: {
        'soft':   '0 1px 2px rgb(0 0 0 / 0.04), 0 8px 32px -8px rgb(0 0 0 / 0.06)',
        'lifted': '0 2px 4px rgb(0 0 0 / 0.04), 0 16px 48px -12px rgb(0 0 0 / 0.12)',
        'float':  '0 4px 16px -4px rgb(0 0 0 / 0.08), 0 24px 64px -16px rgb(0 0 0 / 0.16)',
        'glow':   '0 0 0 1px rgb(var(--accent) / 0.4), 0 8px 32px -4px rgb(var(--accent) / 0.35)',
      },
      backdropBlur: {
        xs: '2px',
      },
      transitionTimingFunction: {
        'out-expo':   'cubic-bezier(0.22, 1, 0.36, 1)',
        'out-elastic':'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'in-out-quart':'cubic-bezier(0.76, 0, 0.24, 1)',
      },
      animation: {
        'rise':        'rise 0.9s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'fade':        'fade 1s ease-out forwards',
        'fade-up':     'fadeUp 1s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'blink':       'blink 1.1s step-end infinite',
        'float':       'float 6s ease-in-out infinite',
        'float-slow':  'float 9s ease-in-out infinite',
        'float-delayed':'float 7s ease-in-out 1.2s infinite',
        'sway':        'sway 5s ease-in-out infinite',
        'spin-slow':   'spin 14s linear infinite',
        'pulse-soft':  'pulseSoft 3.2s ease-in-out infinite',
        'shimmer':     'shimmer 2.4s linear infinite',
        'wiggle':      'wiggle 0.8s ease-in-out',
        'steam':       'steam 4s ease-in-out infinite',
        'leaf-fall':   'leafFall 12s linear infinite',
      },
      keyframes: {
        rise: {
          '0%':   { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fade: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0) rotate(0)' },
          '50%':      { transform: 'translateY(-10px) rotate(1.2deg)' },
        },
        sway: {
          '0%, 100%': { transform: 'rotate(-2deg)' },
          '50%':      { transform: 'rotate(2deg)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.55', transform: 'scale(1)' },
          '50%':      { opacity: '1',    transform: 'scale(1.08)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(0)' },
          '25%':      { transform: 'rotate(-6deg)' },
          '75%':      { transform: 'rotate(6deg)' },
        },
        steam: {
          '0%':   { opacity: '0', transform: 'translateY(0) scale(1)' },
          '30%':  { opacity: '0.55' },
          '100%': { opacity: '0', transform: 'translateY(-28px) scale(1.4)' },
        },
        leafFall: {
          '0%':   { transform: 'translate(0, -12vh) rotate(0deg)',  opacity: '0' },
          '12%':  { opacity: '0.8' },
          '100%': { transform: 'translate(80px, 112vh) rotate(360deg)', opacity: '0' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
