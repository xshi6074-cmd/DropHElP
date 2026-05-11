import tailwindcssAnimate from 'tailwindcss-animate';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts}",
  ],
  theme: {
    extend: {
      // 颜色系统
      colors: {
        // 老人端 - 温暖导向
        elderly: {
          primary: '#07C160',
          'primary-dark': '#06AD56',
          bg: '#FFFDF5',
          surface: '#FFFFFF',
          text: '#2D2D2D',
          'text-secondary': '#666666',
          accent: '#FF9500',
          border: '#E8E8E8',
        },
        // 学生端 - Linear 极简
        student: {
          primary: '#6366F1',
          'primary-dark': '#4F46E5',
          bg: '#FAFAF8',
          surface: '#FFFFFF',
          'surface-hover': '#F4F4F5',
          text: '#18181B',
          'text-secondary': '#71717A',
          'text-muted': '#A1A1AA',
          accent: '#10B981',
          border: '#E4E4E7',
        },
      },
      // 字体大小
      fontSize: {
        // 老人端大字号
        'elderly-xs': ['16px', { lineHeight: '1.5' }],
        'elderly-sm': ['18px', { lineHeight: '1.6' }],
        'elderly-base': ['20px', { lineHeight: '1.6' }],
        'elderly-lg': ['24px', { lineHeight: '1.5' }],
        'elderly-xl': ['28px', { lineHeight: '1.4' }],
        'elderly-2xl': ['32px', { lineHeight: '1.3' }],
        'elderly-3xl': ['48px', { lineHeight: '1.2', letterSpacing: '0.1em' }],
      },
      // 圆角
      borderRadius: {
        'elderly': '16px',
        'elderly-lg': '20px',
        'elderly-xl': '24px',
      },
      // 阴影
      boxShadow: {
        'elderly': '0 2px 8px rgba(0,0,0,0.06)',
        'elderly-lg': '0 4px 12px rgba(7, 193, 96, 0.3)',
        'student': '0 1px 3px rgba(0,0,0,0.1)',
        'student-lg': '0 4px 12px rgba(99, 102, 241, 0.15)',
        'student-hover': '0 8px 24px rgba(99, 102, 241, 0.2)',
      },
      // 间距
      spacing: {
        'elderly-touch': '56px',  // 老人最小触摸区域
      },
      // 动画
      animation: {
        'slide-up': 'slideUp 300ms cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in': 'fadeIn 200ms ease-out',
        'scale-in': 'scaleIn 200ms cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px) scale(0.98)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [
    tailwindcssAnimate,
  ],
}
