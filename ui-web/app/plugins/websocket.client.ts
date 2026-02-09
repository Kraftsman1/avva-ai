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
        errorToasts: [] as CoreError[],
        successToasts: [] as { id: string; message: string }[],
        pendingOps: [] as { id: string; label: string }[],
        conversations: [] as any[],
        currentConversationId: null as string | null,
        currentConversationTitle: 'New Conversation' as string,
        conversationMessages: [] as any[]
    })

    let ws: WebSocket | null = null
    let reconnectTimer: any = null
    const pendingRequests = new Map<string, ReturnType<typeof setTimeout>>()
    const streamingMessages = new Map<string, number>()
    const pendingOperations = new Map<string, { label: string }>()

    const generateId = () => {
        if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
            return crypto.randomUUID()
        }
        return `${Date.now()}-${Math.random().toString(16).slice(2)}`
    }

    const registerRequestTimeout = (requestId: string, context: string) => {
        const timer = setTimeout(() => {
            pendingRequests.delete(requestId)
            pendingOperations.delete(requestId)
            state.pendingOps = Array.from(pendingOperations.entries()).map(([id, op]) => ({
                id,
                label: op.label
            }))
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

    const addSuccessToast = (message: string) => {
        const id = generateId()
        state.successToasts = [...state.successToasts, { id, message }]
        setTimeout(() => {
            state.successToasts = state.successToasts.filter((toast) => toast.id !== id)
        }, 5000)
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
                    const streamIdx = state.messages.findIndex(m => (m as any).streamId === id)
                    if (streamIdx >= 0) {
                        state.messages[streamIdx].text = payload.text
                        state.messages[streamIdx].data = payload.data
                        delete (state.messages[streamIdx] as any).streamId
                    } else {
                        state.messages.push({
                            id: Date.now(),
                            text: payload.text,
                            sender: 'avva',
                            data: payload.data
                        })
                    }
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
                        pendingOperations.delete(id)
                        state.pendingOps = Array.from(pendingOperations.entries()).map(([opId, op]) => ({
                            id: opId,
                            label: op.label
                        }))
                        streamingMessages.delete(id)
                        break
                    }
                    const chunk = payload.chunk || ''
                    const streamIdx = state.messages.findIndex(m => (m as any).streamId === id)
                    if (streamIdx >= 0) {
                        state.messages[streamIdx].text += chunk
                    } else {
                        state.messages.push({
                            id: Date.now(),
                            text: chunk,
                            sender: 'avva',
                            streamId: id
                        })
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
                    if (id && pendingOperations.has(id)) {
                        pendingOperations.delete(id)
                        state.pendingOps = Array.from(pendingOperations.entries()).map(([opId, op]) => ({
                            id: opId,
                            label: op.label
                        }))
                        addSuccessToast('Configuration updated.')
                    }
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
                    if (id && pendingOperations.has(id)) {
                        pendingOperations.delete(id)
                        state.pendingOps = Array.from(pendingOperations.entries()).map(([opId, op]) => ({
                            id: opId,
                            label: op.label
                        }))
                        addSuccessToast('Brain selection updated.')
                    }

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
                    if (id && pendingOperations.has(id)) {
                        pendingOperations.delete(id)
                        state.pendingOps = Array.from(pendingOperations.entries()).map(([opId, op]) => ({
                            id: opId,
                            label: op.label
                        }))
                        addSuccessToast('Brain mode updated.')
                    }
                    break
                case 'settings.data':
                    state.appSettings = payload
                    break
                case 'settings.updated':
                    state.appSettings = { ...state.appSettings, ...payload }
                    if (id && pendingOperations.has(id)) {
                        pendingOperations.delete(id)
                        state.pendingOps = Array.from(pendingOperations.entries()).map(([opId, op]) => ({
                            id: opId,
                            label: op.label
                        }))
                        addSuccessToast('Settings saved.')
                    }
                    break
                case 'conversation.list':
                    state.conversations = payload.sessions || []
                    // Update current title if we have it
                    if (state.currentConversationId) {
                        const currentSession = state.conversations.find((s: any) => s.id === state.currentConversationId)
                        if (currentSession) {
                            state.currentConversationTitle = currentSession.title || 'New Conversation'
                        }
                    }
                    break
                case 'conversation.messages':
                    state.currentConversationId = payload.session?.id || null
                    state.currentConversationTitle = payload.session?.title || 'New Conversation'
                    state.conversationMessages = payload.messages || []
                    // Load messages into the chat
                    state.messages = payload.messages.map((m: any) => ({
                        id: m.id,
                        text: m.content,
                        sender: m.role === 'user' ? 'user' : 'avva',
                        data: m.data || {}
                    }))
                    break
                case 'conversation.started':
                    state.currentConversationId = payload.session_id || null
                    state.currentConversationTitle = 'New Conversation'
                    fetchConversations()
                    break
                case 'conversation.search_results':
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
                    if (id && pendingOperations.has(id)) {
                        pendingOperations.delete(id)
                        state.pendingOps = Array.from(pendingOperations.entries()).map(([opId, op]) => ({
                            id: opId,
                            label: op.label
                        }))
                    }
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
            const requestId = generateId()
            ws.send(JSON.stringify({
                id: requestId,
                type: 'config.update',
                payload: { key, value }
            }))
            pendingOperations.set(requestId, { label: 'Saving configuration' })
            state.pendingOps = Array.from(pendingOperations.entries()).map(([id, op]) => ({
                id,
                label: op.label
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
            const requestId = generateId()
            ws.send(JSON.stringify({
                id: requestId,
                type: 'brains.select',
                payload: { target, brain_id: brainId }
            }))
            pendingOperations.set(requestId, { label: 'Updating brain selection' })
            state.pendingOps = Array.from(pendingOperations.entries()).map(([id, op]) => ({
                id,
                label: op.label
            }))
        }
    }

    const toggleBrainMode = (mode: 'rules_only' | 'auto_selection', enabled: boolean) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const requestId = generateId()
            ws.send(JSON.stringify({
                id: requestId,
                type: 'brains.toggle_mode',
                payload: { mode, enabled }
            }))
            pendingOperations.set(requestId, { label: 'Updating brain mode' })
            state.pendingOps = Array.from(pendingOperations.entries()).map(([id, op]) => ({
                id,
                label: op.label
            }))
        }
    }

    const updateBrainConfig = (brainId: string, config: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const requestId = generateId()
            ws.send(JSON.stringify({
                id: requestId,
                type: 'brains.update_config',
                payload: { brain_id: brainId, config }
            }))
            pendingOperations.set(requestId, { label: 'Saving brain configuration' })
            state.pendingOps = Array.from(pendingOperations.entries()).map(([id, op]) => ({
                id,
                label: op.label
            }))
        }
    }

    const fetchSettings = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ id: generateId(), type: 'settings.get' }))
        }
    }

    const startVoiceCapture = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const requestId = generateId()
            ws.send(JSON.stringify({ id: requestId, type: 'assistant.voice_start' }))
            registerRequestTimeout(requestId, 'assistant.voice_start')
        }
    }

    const updateSettings = (settings: any) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const requestId = generateId()
            ws.send(JSON.stringify({
                id: requestId,
                type: 'settings.update',
                payload: { settings }
            }))
            pendingOperations.set(requestId, { label: 'Saving settings' })
            state.pendingOps = Array.from(pendingOperations.entries()).map(([id, op]) => ({
                id,
                label: op.label
            }))
        }
    }

    const fetchConversations = (limit = 20) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'conversation.list',
                payload: { limit }
            }))
        }
    }

    const loadConversation = (sessionId: string | null = null) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'conversation.get',
                payload: { session_id: sessionId }
            }))
        }
    }

    const deleteConversation = (sessionId: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'conversation.delete',
                payload: { session_id: sessionId }
            }))
            fetchConversations()
        }
    }

    const searchConversations = (query: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'conversation.search',
                payload: { query }
            }))
        }
    }

    const startConversation = (title?: string) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            // Clear current messages
            state.messages = []
            state.currentConversationId = null
            ws.send(JSON.stringify({
                id: generateId(),
                type: 'conversation.start',
                payload: { title }
            }))
            fetchConversations()
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
                startVoiceCapture,
                dismissErrorToast,
                retryError,
                fetchConversations,
                loadConversation,
                deleteConversation,
                searchConversations,
                startConversation
            }
        }
    }
})
