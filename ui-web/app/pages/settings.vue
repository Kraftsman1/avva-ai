<template>
    <div class="flex-1 overflow-y-auto p-6 lg:p-14 font-sans bg-[#000000] selection:bg-ava-purple/30">
        <!-- Breadcrumbs & Meta -->
        <div class="flex items-center justify-between mb-10 animate-in fade-in slide-in-from-top-4 duration-700">
            <div class="flex items-center gap-2 text-[10px] font-black text-white/20 tracking-[0.2em] uppercase">
                <NuxtLink to="/" class="hover:text-ava-purple transition-colors">OS_LAYER</NuxtLink>
                <span class="opacity-30">/</span>
                <span class="text-white/40">CORE_CONFIG</span>
            </div>
            <div class="flex items-center gap-3">
                <div class="h-[1px] w-12 bg-white/5"></div>
                <span class="text-[9px] font-mono text-white/10 tracking-widest">BUILD_24.0.STABLE</span>
            </div>
        </div>

        <!-- Header Section -->
        <div
            class="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-16 animate-in fade-in slide-in-from-left-4 duration-700 delay-100">
            <div class="space-y-4">
                <div class="flex items-center gap-4">
                    <div
                        class="w-12 h-12 rounded-2xl bg-gradient-to-br from-ava-purple to-[#9333ea] flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.3)]">
                        <Settings class="w-6 h-6 text-white" />
                    </div>
                    <h1 class="text-5xl font-black text-white tracking-tighter">System Configuration</h1>
                </div>
                <p class="text-white/30 font-medium text-lg max-w-xl leading-relaxed">
                    Orchestrate the underlying intelligence layers and hardware mapping of your Linux Assistant.
                </p>
            </div>
            <Button variant="outline"
                class="border-white/5 bg-white/[0.02] text-white/40 hover:bg-white/[0.05] hover:text-white gap-3 font-black text-[10px] tracking-[0.2em] uppercase px-8 h-14 rounded-2xl group transition-all"
                @click="refreshAll">
                <RefreshCw class="w-4 h-4 group-hover:rotate-180 transition-transform duration-700" />
                SYNC_STATE
            </Button>
        </div>

        <Tabs v-model="activeTab" class="w-full">
            <div
                class="flex items-center justify-between mb-12 border-b border-white/[0.03] pb-1 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
                <TabsList class="bg-transparent p-0 gap-10 h-auto">
                    <TabsTrigger value="general"
                        class="px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60">
                        01_GENERAL
                    </TabsTrigger>
                    <TabsTrigger value="brains"
                        class="px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60">
                        02_BRAIN_REGISTRY
                    </TabsTrigger>
                    <TabsTrigger value="stack"
                        class="px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60">
                        03_INTEL_STACK
                    </TabsTrigger>
                </TabsList>
            </div>

            <!-- General Settings Tab -->
            <TabsContent value="general" class="animate-in fade-in zoom-in-95 duration-500 outline-none">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
                    <Card class="cyber-card p-10 space-y-10 group">
                        <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4">
                            <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">Identity
                                & Voice</h2>
                        </div>
                        <div class="space-y-8">
                            <div class="space-y-3">
                                <Label
                                    class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Assistant
                                    Identifier</Label>
                                <Input v-model="settings.NAME"
                                    class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6 focus:border-ava-purple/50 focus:bg-white/[0.04] transition-all"
                                    @change="saveSettings" />
                            </div>
                            <div class="space-y-3">
                                <Label
                                    class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Neural
                                    Wake Word</Label>
                                <Input v-model="settings.WAKE_WORD"
                                    class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6 focus:border-ava-purple/50 focus:bg-white/[0.04] transition-all"
                                    @change="saveSettings" />
                            </div>
                            <div class="space-y-3">
                                <Label class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">OS
                                    Language Mapping</Label>
                                <Select v-model="settings.LANGUAGE" @update:modelValue="saveSettings">
                                    <SelectTrigger
                                        class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6 hover:bg-white/[0.04]">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent
                                        class="bg-[#0a0a0f] border-white/10 text-white rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
                                        <SelectItem value="en-uk">English (UK)</SelectItem>
                                        <SelectItem value="en-us">English (US)</SelectItem>
                                        <SelectItem value="es-es">Spanish (ES)</SelectItem>
                                        <SelectItem value="fr-fr">French (FR)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    </Card>

                    <div class="space-y-10">
                        <Card class="cyber-card p-10 space-y-10">
                            <div class="flex items-center gap-4 border-l-2 border-[#34d399] pl-4">
                                <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                    Engine Parameters</h2>
                            </div>
                            <div class="space-y-8">
                                <div class="space-y-3">
                                    <Label
                                        class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Universal
                                        API Access</Label>
                                    <Input v-model="settings.API_KEY" type="password"
                                        class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6 font-mono focus:border-ava-purple/50 transition-all"
                                        placeholder="GEMINI_PRIVATE_KEY_••••••••" @change="saveSettings" />
                                </div>
                                <div class="space-y-3">
                                    <Label
                                        class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Speech
                                        Synthesis Engine</Label>
                                    <Select v-model="settings.TTS_ENGINE" @update:modelValue="saveSettings">
                                        <SelectTrigger
                                            class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent class="bg-[#0a0a0f] border-white/10 text-white rounded-xl">
                                            <SelectItem value="piper">Piper (Native/Local)</SelectItem>
                                            <SelectItem value="gtts">Google Cloud (Cloud)</SelectItem>
                                            <SelectItem value="openai">OpenAI (Cloud)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div v-if="settings.TTS_ENGINE === 'piper'"
                                    class="space-y-3 animate-in slide-in-from-top-2 duration-300">
                                    <Label
                                        class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Acoustic
                                        Model</Label>
                                    <Select v-model="settings.PIPER_VOICE" @update:modelValue="saveSettings">
                                        <SelectTrigger
                                            class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent class="bg-[#0a0a0f] border-white/10 text-white rounded-xl">
                                            <SelectItem value="en_US-lessac-medium.onnx">M_Lessac_Med</SelectItem>
                                            <SelectItem value="en_US-amy-low.onnx">F_Amy_LowRes</SelectItem>
                                            <SelectItem value="en_GB-southern_english_female-low.onnx">F_Southern_UK
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                        </Card>

                        <div class="glass-panel p-6 rounded-3xl flex items-center gap-5 border-white/[0.02]">
                            <div class="p-3 rounded-xl bg-[#34d399]/10 text-[#34d399]">
                                <ShieldCheck class="w-6 h-6" />
                            </div>
                            <div class="flex-1">
                                <h4 class="text-[10px] font-black text-[#34d399] tracking-widest uppercase mb-1">Local
                                    Security Active</h4>
                                <p class="text-[11px] text-white/30 font-bold leading-tight uppercase tracking-tighter">
                                    Your voice data never leaves the local sandbox unless cloud engines are active.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </TabsContent>

            <!-- Brain Manager Tab -->
            <TabsContent value="brains" class="animate-in fade-in zoom-in-95 duration-500 outline-none">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    <div class="lg:col-span-2 space-y-4">
                        <div v-for="(brain, idx) in brains" :key="brain.id"
                            class="cyber-card p-6 flex flex-col sm:flex-row items-center justify-between gap-6 group hover:translate-x-1 animate-in slide-in-from-right-4 duration-500"
                            :style="{ animationDelay: idx * 100 + 'ms' }">
                            <div class="flex items-center gap-6">
                                <div
                                    class="w-16 h-16 rounded-[1.25rem] bg-white/[0.02] border border-white/[0.05] flex items-center justify-center text-ava-purple group-hover:scale-110 transition-transform duration-500 relative">
                                    <Brain v-if="brain.provider !== 'openai'" class="w-8 h-8" />
                                    <Pentagon v-else class="w-8 h-8" />
                                    <div v-if="activeBrainId === brain.id"
                                        class="absolute -top-1 -right-1 w-4 h-4 bg-ava-purple rounded-full border-2 border-[#000000] shadow-[0_0_10px_#7c3aed]">
                                    </div>
                                </div>
                                <div class="space-y-1">
                                    <div class="flex items-center gap-3">
                                        <h3 class="font-black text-lg text-white tracking-tight uppercase">{{ brain.name
                                            }}</h3>
                                        <div
                                            class="px-2 py-0.5 rounded-md bg-white/[0.05] text-[8px] font-black text-white/40 tracking-widest uppercase border border-white/[0.05]">
                                            {{ brain.provider }}</div>
                                    </div>
                                    <div
                                        class="flex items-center gap-4 text-[9px] font-black tracking-[0.15em] uppercase">
                                        <span class="text-white/20">Privacy: <span class="text-white/40">{{
                                                brain.privacy_level }}</span></span>
                                        <span class="w-1 h-1 bg-white/10 rounded-full"></span>
                                        <span class="text-white/20">State: <span
                                                class="text-[#34d399]">OPTIMIZED</span></span>
                                    </div>
                                </div>
                            </div>

                            <div class="flex items-center gap-3">
                                <Button variant="ghost" size="sm"
                                    class="h-10 px-5 font-black text-[9px] tracking-widest uppercase rounded-xl transition-all"
                                    :class="activeBrainId === brain.id ? 'bg-ava-purple text-white cursor-default' : 'text-white/40 hover:text-white hover:bg-white/5 border border-white/5 hover:border-white/10'"
                                    :disabled="activeBrainId === brain.id" @click="setPrimary(brain.id)">
                                    {{ activeBrainId === brain.id ? 'ACTIVE' : 'ACTIVATE' }}
                                </Button>
                                <Button variant="ghost" size="sm"
                                    class="h-10 px-5 font-black text-[9px] tracking-widest uppercase text-white/20 hover:text-white hover:bg-white/5 rounded-xl border border-white/5 transition-all"
                                    :disabled="fallbackBrainId === brain.id" @click="setFallback(brain.id)">
                                    {{ fallbackBrainId === brain.id ? 'FALLBACK_ON' : 'SET_FALLBACK' }}
                                </Button>
                            </div>
                        </div>
                    </div>

                    <div class="space-y-10">
                        <Card class="cyber-card p-10 space-y-10">
                            <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4">
                                <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                    Cognitive Flow</h2>
                            </div>
                            <div class="space-y-10">
                                <div class="flex items-center justify-between group cursor-pointer"
                                    @click="toggleMode('auto_selection', !autoSelection)">
                                    <div class="space-y-1">
                                        <Label
                                            class="text-white font-black text-xs uppercase tracking-widest group-hover:text-ava-purple transition-colors">Neural
                                            Auto-Routing</Label>
                                        <p
                                            class="text-[9px] text-white/20 uppercase tracking-[0.15em] font-black leading-tight">
                                            Switch brains based on query intent</p>
                                    </div>
                                    <Switch :checked="autoSelection" />
                                </div>
                                <Separator class="bg-white/[0.03]" />
                                <div class="flex items-center justify-between group cursor-pointer"
                                    @click="toggleMode('rules_only', !rulesOnly)">
                                    <div class="space-y-1">
                                        <Label
                                            class="text-white font-black text-xs uppercase tracking-widest group-hover:text-ava-purple transition-colors">Offline
                                            Kernel Mode</Label>
                                        <p
                                            class="text-[9px] text-white/20 uppercase tracking-[0.15em] font-black leading-tight">
                                            Bypass LLM for intent-only execution</p>
                                    </div>
                                    <Switch :checked="rulesOnly" />
                                </div>
                            </div>
                        </Card>

                        <div class="glass-panel p-8 rounded-[2.5rem] text-center border-ava-purple/5">
                            <div class="mb-4 inline-flex p-4 rounded-3xl bg-ava-purple/5 text-ava-purple">
                                <Database class="w-8 h-8" />
                            </div>
                            <p
                                class="text-[10px] font-black text-white/30 leading-relaxed uppercase tracking-[0.2em] px-2 italic">
                                AVA Kernel automatically handles intent classification locally for enhanced privacy.
                            </p>
                        </div>
                    </div>
                </div>
            </TabsContent>

            <!-- Intelligence Stack Tab -->
            <TabsContent value="stack" class="animate-in fade-in zoom-in-95 duration-500 outline-none">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    <div class="lg:col-span-2 space-y-10">
                        <Card class="cyber-card p-10 space-y-10">
                            <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4">
                                <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                    Inference Parameters</h2>
                            </div>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-10 mb-6">
                                <div class="space-y-3">
                                    <Label
                                        class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Stack
                                        Provider</Label>
                                    <Select v-model="configValue.LLM_PROVIDER"
                                        @update:modelValue="saveConfigSetting('LLM_PROVIDER', $event)">
                                        <SelectTrigger
                                            class="bg-white/[0.02] border-white/5 text-white h-16 rounded-2xl px-6 hover:bg-white/[0.04]">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent class="bg-[#0a0a0f] border-white/10 text-white rounded-xl">
                                            <SelectItem value="google">Google Gemini Pro (Cloud)</SelectItem>
                                            <SelectItem value="ollama">Ollama Llama Hub (Local)</SelectItem>
                                            <SelectItem value="openai">OpenAI Neural API (Cloud)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div class="space-y-3">
                                    <Label
                                        class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Active
                                        Neural Weights</Label>
                                    <Select v-model="configValue.MODEL_NAME"
                                        @update:modelValue="saveConfigSetting('MODEL_NAME', $event)">
                                        <SelectTrigger
                                            class="bg-white/[0.02] border-white/5 text-white h-16 rounded-2xl px-6 hover:bg-white/[0.04]">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent class="bg-[#0a0a0f] border-white/10 text-white rounded-xl">
                                            <SelectItem value="gemini-1.5-flash">Gemini Flash v1.5</SelectItem>
                                            <SelectItem value="llama3:8b">Llama 3 Instruct (8B)</SelectItem>
                                            <SelectItem value="llama3:70b">Llama 3 Frontier (70B)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <!-- Sliders -->
                            <div class="space-y-12 pb-4">
                                <div class="space-y-6">
                                    <div class="flex justify-between items-end px-1">
                                        <div class="space-y-1">
                                            <Label
                                                class="text-[10px] font-black text-white/40 tracking-[0.2em] uppercase">Spectral
                                                Temperature</Label>
                                            <p
                                                class="text-[9px] text-white/10 font-black uppercase tracking-widest italic">
                                                Controls creativity vs precision</p>
                                        </div>
                                        <span class="text-ava-purple font-mono font-black text-xl tabular-nums">{{
                                            temp[0].toFixed(2) }}</span>
                                    </div>
                                    <Slider v-model="temp" :max="1" :step="0.01" class="py-2 spectral-slider"
                                        @update:modelValue="saveConfigSetting('TEMPERATURE', temp[0])" />
                                </div>

                                <div class="space-y-6">
                                    <div class="flex justify-between items-end px-1">
                                        <div class="space-y-1">
                                            <Label
                                                class="text-[10px] font-black text-white/40 tracking-[0.2em] uppercase">Context
                                                Buffer Window</Label>
                                            <p
                                                class="text-[9px] text-white/10 font-black uppercase tracking-widest italic">
                                                Allocation of VRAM for conversation memory</p>
                                        </div>
                                        <span class="text-ava-purple font-mono font-black text-xl tabular-nums">{{
                                            context[0].toLocaleString() }}</span>
                                    </div>
                                    <Slider v-model="context" :max="32768" :step="1024" class="py-2 spectral-slider"
                                        @update:modelValue="saveConfigSetting('CONTEXT_WINDOW', context[0])" />
                                </div>
                            </div>
                        </Card>

                        <Card class="cyber-card p-10 space-y-10">
                            <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4">
                                <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                    Filesystem Mapping</h2>
                            </div>

                            <div class="space-y-10">
                                <div class="space-y-3">
                                    <Label
                                        class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Kernel
                                        Model Path</Label>
                                    <div class="relative group">
                                        <Input v-model="modelPath"
                                            class="bg-white/[0.02] border-white/5 text-[#a78bfa] font-mono h-14 rounded-2xl px-6 focus:border-ava-purple/50 pr-12 transition-all hover:bg-white/[0.04]"
                                            @change="saveConfigSetting('MODEL_PATH', modelPath)" />
                                        <Folder
                                            class="absolute right-5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/10 group-hover:text-ava-purple transition-colors" />
                                    </div>
                                </div>

                                <div class="space-y-3">
                                    <Label
                                        class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Vector
                                        DB Target</Label>
                                    <div class="relative group">
                                        <Input v-model="dbPath"
                                            class="bg-white/[0.02] border-white/5 text-[#a78bfa] font-mono h-14 rounded-2xl px-6 focus:border-ava-purple/50 pr-12 transition-all hover:bg-white/[0.04]"
                                            @change="saveConfigSetting('DB_PATH', dbPath)" />
                                        <HardDrive
                                            class="absolute right-5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/10 group-hover:text-ava-purple transition-colors" />
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </div>

                    <div class="space-y-10">
                        <!-- Acceleration Card -->
                        <Card class="cyber-card p-10 space-y-10 overflow-hidden relative border-ava-purple/20">
                            <div class="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
                                <Pentagon class="w-32 h-32 text-ava-purple rotate-12" />
                            </div>
                            <div class="flex justify-between items-center relative z-10">
                                <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                    Telemetry</h2>
                                <div class="flex items-center gap-2">
                                    <div class="w-1.5 h-1.5 bg-[#34d399] rounded-full neon-pulse"></div>
                                    <span
                                        class="text-[9px] font-black text-[#34d399] tracking-widest uppercase">REAL_TIME</span>
                                </div>
                            </div>

                            <div class="space-y-10 relative z-10">
                                <!-- NPU -->
                                <div class="space-y-4">
                                    <div
                                        class="flex justify-between items-center text-[10px] font-black tracking-widest uppercase">
                                        <span class="text-white/30 italic">NPU Acceleration</span>
                                        <span class="text-ava-purple tabular-nums">{{ intStats.npu_acceleration
                                            }}%</span>
                                    </div>
                                    <div
                                        class="h-1.5 w-full bg-white/[0.03] rounded-full overflow-hidden p-[1px] border border-white/[0.05]">
                                        <div class="h-full bg-gradient-to-r from-ava-purple to-[#9333ea] rounded-full shadow-[0_0_15px_rgba(124,58,237,0.5)] transition-all duration-1000"
                                            :style="{ width: intStats.npu_acceleration + '%' }"></div>
                                    </div>
                                </div>

                                <!-- VRAM -->
                                <div class="space-y-4">
                                    <div
                                        class="flex justify-between items-center text-[10px] font-black tracking-widest uppercase">
                                        <span class="text-white/30 italic">Neural VRAM Pool</span>
                                        <span class="text-ava-purple tabular-nums">{{ vramFormatted }}</span>
                                    </div>
                                    <div
                                        class="h-1.5 w-full bg-white/[0.03] rounded-full overflow-hidden p-[1px] border border-white/[0.05]">
                                        <div class="h-full bg-gradient-to-r from-ava-purple to-[#9333ea] rounded-full shadow-[0_0_15px_rgba(124,58,237,0.5)] transition-all duration-1000"
                                            :style="{ width: sysStats.vram + '%' }"></div>
                                    </div>
                                </div>

                                <div class="grid grid-cols-2 gap-4 mt-4">
                                    <div
                                        class="glass-panel p-6 rounded-3xl text-center space-y-2 border-white/[0.01] hover:bg-white/[0.03] transition-all">
                                        <div class="text-[8px] font-black text-white/10 tracking-[0.2em] uppercase">
                                            TOKEN_FLOW</div>
                                        <div class="text-3xl font-black text-white tracking-tighter tabular-nums">{{
                                            intStats.tokens_sec }}<span class="text-xs text-white/20 ml-1">s</span>
                                        </div>
                                    </div>
                                    <div
                                        class="glass-panel p-6 rounded-3xl text-center space-y-2 border-white/[0.01] hover:bg-white/[0.03] transition-all">
                                        <div class="text-[8px] font-black text-white/10 tracking-[0.2em] uppercase">
                                            LATENCY</div>
                                        <div class="text-3xl font-black text-white tracking-tighter tabular-nums">{{
                                            intStats.latency }}<span class="text-xs text-white/20 ml-1">ms</span></div>
                                    </div>
                                </div>
                            </div>
                        </Card>

                        <!-- Actions -->
                        <div class="space-y-4">
                            <Button
                                class="w-full h-16 rounded-[2rem] bg-ava-purple hover:bg-[#6d28d9] text-white font-black text-[10px] tracking-[0.25em] uppercase shadow-[0_15px_40px_rgba(124,58,237,0.2)] gap-4 transition-all hover:-translate-y-1">
                                <Database class="w-4 h-4" />
                                REBUILD_VECTOR_CORE
                            </Button>
                            <Button variant="outline"
                                class="w-full h-16 rounded-[2rem] border-white/5 bg-white/[0.02] text-white/30 hover:bg-white/[0.05] hover:text-white font-black text-[10px] tracking-[0.25em] uppercase gap-4 transition-all">
                                <Download class="w-4 h-4" />
                                PULL_NEURAL_WEIGHTS
                            </Button>
                        </div>
                    </div>
                </div>
            </TabsContent>
        </Tabs>

        <!-- Footer Stats -->
        <div
            class="mt-20 pt-10 border-t border-white/[0.03] flex flex-col md:flex-row justify-between items-center gap-6 text-[9px] font-black tracking-[0.3em] text-white/10 uppercase">
            <div class="flex items-center gap-8">
                <div class="flex items-center gap-3">
                    <div class="w-1.5 h-1.5 bg-[#34d399] rounded-full animate-pulse shadow-[0_0_8px_#34d39966]"></div>
                    KERNEL: OLLAMA/v0.1.32
                </div>
                <div class="opacity-50">DRIVER: NVIDIA_CUDA_12.4.X</div>
            </div>
            <div class="hover:text-white/40 transition-colors cursor-help">AVA_INTEL_SYSTEM_V2.5.0-STABLE.ARC_64</div>
        </div>
    </div>
</template>

<script setup>
import {
    RefreshCw, Folder, Settings, Cpu,
    ShieldCheck, Database, Download, Brain,
    Pentagon, HardDrive
} from 'lucide-vue-next'

const { $ava } = useNuxtApp()

const activeTab = ref('general')

// Websocket State
const configValue = computed(() => $ava?.state?.config || {})
const sysStats = computed(() => $ava?.state?.systemStats || { cpu: 0, ram: 0, vram: 0, vram_used: 0, vram_total: 0 })
const intStats = computed(() => $ava?.state?.intelligenceStats || { tokens_sec: 0, latency: 0, npu_acceleration: 0 })
const brains = computed(() => $ava?.state?.brains || [])
const activeBrainId = computed(() => $ava?.state?.activeBrainId)
const fallbackBrainId = computed(() => $ava?.state?.fallbackBrainId)
const rulesOnly = computed(() => $ava?.state?.rulesOnly)
const autoSelection = computed(() => $ava?.state?.autoSelection)
const appSettings = computed(() => $ava?.state?.appSettings || {})

// Local Form State
const settings = reactive({
    NAME: '',
    WAKE_WORD: '',
    LANGUAGE: 'en-uk',
    TTS_ENGINE: 'gtts',
    PIPER_VOICE: 'en_US-lessac-medium.onnx',
    API_KEY: '',
    OPENAI_API_KEY: ''
})

// Sync local form when appSettings load
watch(appSettings, (newVal) => {
    Object.keys(settings).forEach(key => {
        if (newVal[key] !== undefined) settings[key] = newVal[key]
    })
}, { immediate: true, deep: true })

// Intelligence Stack Local state
const temp = ref([0.72])
const context = ref([8192])
const modelPath = ref('/home/user/.local/share/ava/models/llama3-8b.gguf')
const dbPath = ref('/var/lib/ava/chromadb/knowledge_base_01')

// Sync local refs when config loads
watch(configValue, (newVal) => {
    if (newVal.TEMPERATURE !== undefined) temp.value = [newVal.TEMPERATURE]
    if (newVal.CONTEXT_WINDOW !== undefined) context.value = [newVal.CONTEXT_WINDOW]
    if (newVal.MODEL_PATH) modelPath.value = newVal.MODEL_PATH
    if (newVal.DB_PATH) dbPath.value = newVal.DB_PATH
}, { immediate: true, deep: true })

// Actions
const saveSettings = () => {
    $ava.updateSettings({ ...settings })
}

const saveConfigSetting = (key, value) => {
    $ava.updateConfig(key, value)
}

const setPrimary = (id) => {
    $ava.selectBrain('active', id)
}

const setFallback = (id) => {
    $ava.selectBrain('fallback', id)
}

const toggleMode = (mode, enabled) => {
    $ava.toggleBrainMode(mode, enabled)
}

const refreshAll = () => {
    $ava.fetchConfig()
    $ava.fetchBrains()
    $ava.fetchSettings()
}

onMounted(() => {
    refreshAll()
})

const vramFormatted = computed(() => {
    if (sysStats.value.vram_total) {
        const used = (sysStats.value.vram_used / 1024).toFixed(1)
        const total = (sysStats.value.vram_total / 1024).toFixed(1)
        return `${used} / ${total}GB`
    }
    return '0.0 / 0.0GB'
})
</script>

<style scoped>
/* Spectral Slider Styling */
:deep(.spectral-slider) {
    @apply h-12 flex items-center;
}

:deep(.relative.w-full.touch-none.select-none.flex.items-center) {
    height: 2.5rem;
}

:deep([role="slider"]) {
    width: 1.5rem;
    height: 1.5rem;
    background-color: #ffffff;
    border: 3px solid #7c3aed;
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.6), inset 0 0 10px rgba(0, 0, 0, 0.2);
    border-radius: 0.5rem;
    cursor: ew-resize;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep([role="slider"]:hover) {
    transform: scale(1.15);
    background-color: #7c3aed;
    border-color: #ffffff;
}

:deep([role="slider"]:active) {
    transform: scale(0.9);
}

:deep([role="track"]) {
    height: 0.25rem;
    background-color: rgba(255, 255, 255, 0.02);
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.03);
}

:deep(.bg-primary) {
    background: linear-gradient(90deg, #7c3aed, #9333ea);
    box-shadow: 0 0 10px rgba(124, 58, 237, 0.3);
}

/* Custom Select Styling Overrides */
:deep([role="combobox"]) {
    @apply transition-all duration-300;
}

:deep([role="combobox"]:focus) {
    @apply ring-1 ring-ava-purple/50 border-ava-purple/30 bg-white/[0.04];
}

/* Smooth Scrolling */
.overflow-y-auto {
    scrollbar-gutter: stable;
}

/* Glass Tabs Override */
:deep([role="tablist"]) {
    @apply border-none;
}
</style>
