/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./components/**/*.{js,vue,ts}",
        "./layouts/**/*.vue",
        "./pages/**/*.vue",
        "./plugins/**/*.{js,ts}",
        "./app.vue",
        "./error.vue",
    ],
    theme: {
        extend: {
            colors: {
                'ava-bg': '#0c0c14',
                'ava-bg-sidebar': '#11111b',
                'ava-bg-elevated': '#181826',
                'ava-bg-code': '#08080f',
                'ava-purple': {
                    DEFAULT: '#a855f7',
                    600: '#9333ea',
                    700: '#7c3aed',
                    800: '#6b21a8',
                    900: '#581c87',
                },
                'ava-neon': '#34d399', // Cyan/Emerald from the design
                'ava-border': '#1e1e2e',
                'ava-border-glow': 'rgba(168, 85, 247, 0.15)',
                'ava-text': '#e2e2e9',
                'ava-text-muted': '#71717a',
                'ava-text-bright': '#fafafa',
            },
            fontFamily: {
                'sans': ['Inter', 'system-ui', 'sans-serif'],
                'mono': ['Fira Code', 'monospace'],
            },
            boxShadow: {
                'cyber': '0 0 20px rgba(168, 85, 247, 0.15)',
                'cyber-strong': '0 0 40px rgba(168, 85, 247, 0.3)',
            },
            borderRadius: {
                'ava': '16px',
                'ava-sm': '8px',
            }
        },
    },
    plugins: [],
}
