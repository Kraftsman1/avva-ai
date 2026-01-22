export default defineNuxtPlugin(() => {
    interface Message {
        id: number
        text: string
        sender: 'user' | 'avva'
        data?: any
    }

    const state = reactive({
        assistantState: 'idle',
        messages: [] as Message[],
        systemStats: { cpu: 0, ram: 0, vram: 0 },
        activeModel: 'Llama-3-8B-Instruct',
        isConnected: false
    })

    let ws: WebSocket | null = null
    let reconnectTimer: any = null

    const connect = () => {
        if (typeof window === 'undefined') return

        console.log('🔌 Connecting to AVA Core WebSocket...')
        ws = new WebSocket('ws://localhost:8765')

        ws.onopen = () => {
            state.isConnected = true
            console.log('✅ Connected to AVA Core')
            if (reconnectTimer) clearTimeout(reconnectTimer)
        }

        ws.onmessage = (event: MessageEvent) => {
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
                    state.messages.push({
                        id: Date.now(),
                        text: payload.command,
                        sender: 'user'
                    })
                    break
                case 'system.stats':
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

    const sendCommand = (command: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            // We no longer push locally here to avoid duplication.
            // The server will broadcast the command back to us.
            ws.send(JSON.stringify({
                type: 'assistant.command',
                payload: { command }
            }))
        }
    }

    // Auto-connect on client init
    if (typeof window !== 'undefined') {
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
