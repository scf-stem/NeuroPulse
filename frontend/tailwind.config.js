/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 震颤卫士品牌色 - 珊瑚橙 (Coral Orange)
        primary: {
          50: '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
          700: '#C2410C',
          800: '#9A3412',
          900: '#7C2D12',
        },
        // 柔和紫 (AI功能)
        lavender: {
          50: '#FAF5FF',
          100: '#F3E8FF',
          200: '#E9D5FF',
          300: '#D8B4FE',
          400: '#C084FC',
          500: '#A855F7',
          600: '#9333EA',
          700: '#7C3AED',
          800: '#6D28D9',
          900: '#5B21B6',
        },
        // 清新绿 (成功状态)
        mint: {
          50: '#ECFDF5',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          800: '#065F46',
          900: '#064E3B',
        },
        // 温暖灰色扩展 (用于深色主题)
        warmGray: {
          50: '#FDFCFB',
          100: '#FBF9F7',
          200: '#F5F2EE',
          300: '#EDE8E3',
          400: '#D6CFC7',
          500: '#B8ADA1',
          600: '#8B7E72',
          700: '#5F5549',
          800: '#3D362E',
          900: '#1F1B17',
        },
        // 严重度颜色 - 保持医学直觉性
        severity: {
          0: '#22C55E', // 无震颤 - 绿色
          1: '#84CC16', // 轻度 - 青绿
          2: '#FACC15', // 中轻度 - 黄色
          3: '#FB923C', // 中度 - 橙色
          4: '#F87171', // 重度 - 柔和红
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(249, 115, 22, 0.1), 0 4px 6px -4px rgba(249, 115, 22, 0.1)',
        'soft-lg': '0 10px 40px -10px rgba(249, 115, 22, 0.15)',
        'soft-xl': '0 20px 50px -15px rgba(249, 115, 22, 0.2)',
        'glow': '0 0 20px rgba(249, 115, 22, 0.3)',
        'glow-lg': '0 0 40px rgba(249, 115, 22, 0.4)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'warm-gradient': 'linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 50%, #FEF3E2 100%)',
        'coral-gradient': 'linear-gradient(135deg, #FB923C 0%, #F97316 50%, #EA580C 100%)',
        'lavender-gradient': 'linear-gradient(135deg, #E9D5FF 0%, #D8B4FE 50%, #C084FC 100%)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'slide-in-right': 'slideInRight 0.3s ease-out forwards',
        'slide-in-left': 'slideInLeft 0.3s ease-out forwards',
        'scale-in': 'scaleIn 0.2s ease-out forwards',
        'pulse-ring': 'pulseRing 2s ease-out infinite',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'bounce-soft': 'bounceSoft 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseRing: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(1.5)', opacity: '0' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      transitionTimingFunction: {
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
    },
  },
  plugins: [],
}
