export default defineNuxtPlugin(() => {
    const state = reactive({
        assistantState: 'idle',
        messages: [],
        systemStats: { cpu: 0, ram: 0, vram: 0 },
        activeModel: 'Llama-3-8B-Instruct',
        isConnected: false
    })

    let ws = null
    let reconnectTimer = null

    const connect = () => {
        if (process.server) return

        console.log('🔌 Connecting to AVA Core WebSocket...')
        ws = new WebSocket('ws://localhost:8765')

        ws.onopen = () => {
            state.isConnected = true
            console.log('✅ Connected to AVA Core')
            clearTimeout(reconnectTimer)
        }

        ws.onmessage = (event) => {
            const { type, payload } = JSON.parse(event.data)

            switch (type) {
                case 'assistant.state':
                    state.assistantState = payload.state
                    break
                case 'assistant.response':
                    state.messages.push({
                        id: Date.now(),
                        text: payload.text,
                        sender: 'avva',
                        data: payload.data
                    })
                    break
                case 'assistant.command':
                    // Also track commands sent from other clients if needed
                    break
                case 'system.stats': // We'll add this broadcast to the core later
                    state.systemStats = payload
                    break
            }
        }

        ws.onclose = () => {
            state.isConnected = false
            console.log('❌ Disconnected from AVA Core. Retrying in 3s...')
            reconnectTimer = setTimeout(connect, 3000)
        }

        ws.onerror = (err) => {
            console.error('WebSocket Error:', err)
        }
    }

    const sendCommand = (command) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            // Add local message immediately for responsiveness
            state.messages.push({
                id: Date.now(),
                text: command,
                sender: 'user'
            })

            ws.send(JSON.stringify({
                type: 'assistant.command',
                payload: { command }
            }))
        }
    }

    // Auto-connect on client init
    if (process.client) {
        connect()
    }

    return {
        provide: {
            ava: {
                state,
                sendCommand
            }
        }
    }
})
