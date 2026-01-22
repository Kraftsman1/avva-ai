/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
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
    				'600': '#9333ea',
    				'700': '#7c3aed',
    				'800': '#6b21a8',
    				'900': '#581c87',
    				DEFAULT: '#a855f7'
    			},
    			'ava-neon': '#34d399',
    			'ava-border': '#1e1e2e',
    			'ava-border-glow': 'rgba(168, 85, 247, 0.15)',
    			'ava-text': '#e2e2e9',
    			'ava-text-muted': '#71717a',
    			'ava-text-bright': '#fafafa',
    			background: 'hsl(var(--background))',
    			foreground: 'hsl(var(--foreground))',
    			card: {
    				DEFAULT: 'hsl(var(--card))',
    				foreground: 'hsl(var(--card-foreground))'
    			},
    			popover: {
    				DEFAULT: 'hsl(var(--popover))',
    				foreground: 'hsl(var(--popover-foreground))'
    			},
    			primary: {
    				DEFAULT: 'hsl(var(--primary))',
    				foreground: 'hsl(var(--primary-foreground))'
    			},
    			secondary: {
    				DEFAULT: 'hsl(var(--secondary))',
    				foreground: 'hsl(var(--secondary-foreground))'
    			},
    			muted: {
    				DEFAULT: 'hsl(var(--muted))',
    				foreground: 'hsl(var(--muted-foreground))'
    			},
    			accent: {
    				DEFAULT: 'hsl(var(--accent))',
    				foreground: 'hsl(var(--accent-foreground))'
    			},
    			destructive: {
    				DEFAULT: 'hsl(var(--destructive))',
    				foreground: 'hsl(var(--destructive-foreground))'
    			},
    			border: 'hsl(var(--border))',
    			input: 'hsl(var(--input))',
    			ring: 'hsl(var(--ring))',
    			chart: {
    				'1': 'hsl(var(--chart-1))',
    				'2': 'hsl(var(--chart-2))',
    				'3': 'hsl(var(--chart-3))',
    				'4': 'hsl(var(--chart-4))',
    				'5': 'hsl(var(--chart-5))'
    			}
    		},
    		fontFamily: {
    			sans: [
    				'Inter',
    				'system-ui',
    				'sans-serif'
    			],
    			mono: [
    				'Fira Code',
    				'monospace'
    			]
    		},
    		boxShadow: {
    			cyber: '0 0 20px rgba(168, 85, 247, 0.15)',
    			'cyber-strong': '0 0 40px rgba(168, 85, 247, 0.3)'
    		},
    		borderRadius: {
    			ava: '16px',
    			'ava-sm': '8px',
    			lg: 'var(--radius)',
    			md: 'calc(var(--radius) - 2px)',
    			sm: 'calc(var(--radius) - 4px)'
    		}
    	}
    },
    plugins: [require("tailwindcss-animate")],
}
