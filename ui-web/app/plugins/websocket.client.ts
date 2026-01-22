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
        systemStats: { cpu: 0, ram: 0, vram: 0, vram_used: 0, vram_total: 0 },
        intelligenceStats: { tokens_sec: 0, latency: 0, npu_acceleration: 0 },
        config: {} as any,
        brains: [] as any[],
        activeBrainId: null as string | null,
        fallbackBrainId: null as string | null,
        rulesOnly: false,
        autoSelection: true,
        appSettings: {} as any,
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
            // Initial data pull
            fetchConfig()
            fetchBrains()
            fetchSettings()
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
                case 'intelligence.stats':
                    state.intelligenceStats = payload
                    break
                case 'config.data':
                    state.config = payload
                    break
                case 'config.updated':
                    state.config = { ...state.config, ...payload }
                    break
                case 'brains.data':
                    state.brains = payload.brains
                    state.activeBrainId = payload.active_id
                    state.fallbackBrainId = payload.fallback_id
                    state.rulesOnly = payload.rules_only
                    state.autoSelection = payload.auto_selection

                    // Sync active model name
                    if (state.activeBrainId) {
                        const activeBrain = state.brains.find((b: any) => b.id === state.activeBrainId)
                        if (activeBrain) {
                            // Check config_data first for specific model
                            if (activeBrain.config_data?.model) {
                                state.activeModel = activeBrain.config_data.model
                            } else {
                                state.activeModel = activeBrain.name || activeBrain.provider
                            }
                        }
                    }
                    break
                case 'brains.updated':
                    state.activeBrainId = payload.active_id
                    state.fallbackBrainId = payload.fallback_id

                    // Sync active model name
                    if (state.activeBrainId) {
                        const activeBrain = state.brains.find((b: any) => b.id === state.activeBrainId)
                        if (activeBrain) {
                            // Check config_data first for specific model
                            if (activeBrain.config_data?.model) {
                                state.activeModel = activeBrain.config_data.model
                            } else {
                                state.activeModel = activeBrain.name || activeBrain.provider
                            }
                        }
                    }
                    break
                case 'brains.mode_updated':
                    state.rulesOnly = payload.rules_only
                    state.autoSelection = payload.auto_selection
                    break
                case 'settings.data':
                    state.appSettings = payload
                    break
                case 'settings.updated':
                    state.appSettings = { ...state.appSettings, ...payload }
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
            ws.send(JSON.stringify({
                type: 'assistant.command',
                payload: { command }
            }))
        }
    }

    const fetchConfig = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'config.get' }))
        }
    }

    const updateConfig = (key: string, value: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'config.update',
                payload: { key, value }
            }))
        }
    }

    const fetchBrains = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'brains.list' }))
        }
    }

    const selectBrain = (target: 'active' | 'fallback', brainId: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'brains.select',
                payload: { target, brain_id: brainId }
            }))
        }
    }

    const toggleBrainMode = (mode: 'rules_only' | 'auto_selection', enabled: boolean) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'brains.toggle_mode',
                payload: { mode, enabled }
            }))
        }
    }

    const updateBrainConfig = (brainId: string, config: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'brains.update_config',
                payload: { brain_id: brainId, config }
            }))
        }
    }

    const fetchSettings = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'settings.get' }))
        }
    }

    const updateSettings = (settings: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'settings.update',
                payload: { settings }
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
                sendCommand,
                fetchConfig,
                updateConfig,
                fetchBrains,
                selectBrain,
                toggleBrainMode,
                updateBrainConfig,
                fetchSettings,
                updateSettings
            }
        }
    }
})
