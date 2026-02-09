export default defineNuxtPlugin(() => {
    interface Message {
        id: number
        text: string
        sender: 'user' | 'avva'
        data?: any
    }

    interface CoreError {
        id: string
        code: string
        message: string
        severity: 'error' | 'warning' | 'info'
        retry_allowed: boolean
        context?: Record<string, any>
        timestamp: string
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
        isConnected: false,
        errorLog: [] as CoreError[],
        errorToasts: [] as CoreError[]
    })

    let ws: WebSocket | null = null
    let reconnectTimer: any = null
    const pendingRequests = new Map<string, ReturnType<typeof setTimeout>>()
    const streamingMessages = new Map<string, number>()

    const generateId = () => {
        if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
            return crypto.randomUUID()
        }
        return `${Date.now()}-${Math.random().toString(16).slice(2)}`
    }

    const registerRequestTimeout = (requestId: string, context: string) => {
        const timer = setTimeout(() => {
            pendingRequests.delete(requestId)
            state.messages.push({
                id: Date.now(),
                text: `Request timed out after 30s. (${context})`,
                sender: 'avva',
                data: { error: true, requestId }
            })
        }, 30000)
        pendingRequests.set(requestId, timer)
    }

    const pushErrorLog = (entry: CoreError) => {
        state.errorLog = [entry, ...state.errorLog].slice(0, 50)
    }

    const addErrorToast = (entry: CoreError) => {
        state.errorToasts = [...state.errorToasts, entry]
        setTimeout(() => {
            state.errorToasts = state.errorToasts.filter((toast) => toast.id !== entry.id)
        }, 8000)
    }

    const dismissErrorToast = (id: string) => {
        state.errorToasts = state.errorToasts.filter((toast) => toast.id !== id)
    }

    const retryError = (entry: CoreError) => {
        const command = entry.context?.command
        if (command) {
            sendCommand(command)
        }
        dismissErrorToast(entry.id)
    }

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
            const { type, payload, id, timestamp } = JSON.parse(event.data)

            switch (type) {
                case 'assistant.state':
                    state.assistantState = payload.state
                    break
                case 'assistant.response':
                    if (id && pendingRequests.has(id)) {
                        clearTimeout(pendingRequests.get(id))
                        pendingRequests.delete(id)
                    }
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
                case 'assistant.stream': {
                    if (!id) break
                    if (payload.done) {
                        if (pendingRequests.has(id)) {
                            clearTimeout(pendingRequests.get(id))
                            pendingRequests.delete(id)
                        }
                        streamingMessages.delete(id)
                        break
                    }
                    const chunk = payload.chunk || ''
                    if (!streamingMessages.has(id)) {
                        state.messages.push({
                            id: Date.now(),
                            text: chunk,
                            sender: 'avva'
                        })
                        streamingMessages.set(id, state.messages.length - 1)
                    } else {
                        const index = streamingMessages.get(id)
                        const message = state.messages[index]
                        if (message) {
                            message.text += chunk
                        }
                    }
                    break
                }
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
                case 'core.error': {
                    const errorEntry: CoreError = {
                        id: id || generateId(),
                        code: payload.code,
                        message: payload.message,
                        severity: payload.severity || 'error',
                        retry_allowed: Boolean(payload.retry_allowed),
                        context: payload.context || {},
                        timestamp: timestamp || new Date().toISOString()
                    }
                    pushErrorLog(errorEntry)
                    addErrorToast(errorEntry)
                    break
                }
            }
        }

        ws.onclose = () => {
            state.isConnected = false
            pendingRequests.forEach((timer) => clearTimeout(timer))
            pendingRequests.clear()
            console.log('❌ Disconnected from AVA Core. Retrying in 3s...')
            reconnectTimer = setTimeout(connect, 3000)
        }

        ws.onerror = (err) => {
            console.error('WebSocket Error:', err)
        }
    }

    const sendCommand = (command: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const requestId = generateId()
            ws.send(JSON.stringify({
                id: requestId,
                type: 'assistant.command',
                payload: { command }
            }))
            registerRequestTimeout(requestId, `assistant.command "${command}"`)
        }
    }

    const fetchConfig = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ id: generateId(), type: 'config.get' }))
        }
    }

    const updateConfig = (key: string, value: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'config.update',
                payload: { key, value }
            }))
        }
    }

    const fetchBrains = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ id: generateId(), type: 'brains.list' }))
        }
    }

    const selectBrain = (target: 'active' | 'fallback', brainId: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'brains.select',
                payload: { target, brain_id: brainId }
            }))
        }
    }

    const toggleBrainMode = (mode: 'rules_only' | 'auto_selection', enabled: boolean) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'brains.toggle_mode',
                payload: { mode, enabled }
            }))
        }
    }

    const updateBrainConfig = (brainId: string, config: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'brains.update_config',
                payload: { brain_id: brainId, config }
            }))
        }
    }

    const fetchSettings = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ id: generateId(), type: 'settings.get' }))
        }
    }

    const updateSettings = (settings: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
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
                updateSettings,
                dismissErrorToast,
                retryError
            }
        }
    }
})
