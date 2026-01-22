<template>
    <div class="h-full w-full overflow-y-auto p-6 lg:p-14 font-sans bg-[#000000] selection:bg-ava-purple/30">
        <!-- Breadcrumbs & Meta -->
        <div class="flex items-center justify-between mb-10 animate-in fade-in slide-in-from-top-4 duration-700">
            <div class="flex items-center gap-2 text-[10px] font-black text-white/20 tracking-[0.2em] uppercase">
                <NuxtLink to="/" class="hover:text-ava-purple transition-colors">OS_LAYER</NuxtLink>
                <span class="opacity-30">/</span>
                <span class="text-white/40">INTEL_STACK_CORE</span>
            </div>
            <div class="flex items-center gap-3">
                <div class="h-[1px] w-12 bg-white/5"></div>
                <span class="text-[9px] font-mono text-white/10 tracking-widest">LAYER_VISUALIZER_STABLE</span>
            </div>
        </div>

        <!-- Header Section -->
        <div
            class="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-16 animate-in fade-in slide-in-from-left-4 duration-700 delay-100">
            <div class="space-y-4">
                <div class="flex items-center gap-4">
                    <div
                        class="w-12 h-12 rounded-2xl bg-gradient-to-br from-ava-purple to-[#9333ea] flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.3)]">
                        <Cpu class="w-6 h-6 text-white" />
                    </div>
                    <h1 class="text-5xl font-black text-white tracking-tighter italic">Intelligence Stack</h1>
                </div>
                <p class="text-white/30 font-medium text-lg max-w-xl leading-relaxed">
                    Tuning the neural kernel and hardware acceleration for optimal local-first response.
                </p>
            </div>
            <div class="flex gap-4">
                <Button variant="outline"
                    class="border-white/5 bg-white/[0.02] text-white/40 hover:bg-white/[0.05] hover:text-white gap-3 font-black text-[10px] tracking-[0.2em] uppercase px-8 h-14 rounded-2xl group transition-all"
                    @click="refreshAll">
                    <RefreshCw class="w-4 h-4 group-hover:rotate-180 transition-transform duration-700" />
                    RECALIBRATE
                </Button>
            </div>
        </div>

        <Tabs v-model="activeTab" class="w-full">
            <div
                class="flex items-center justify-between mb-12 border-b border-white/[0.03] pb-1 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
                <TabsList class="bg-transparent p-0 gap-10 h-auto">
                    <TabsTrigger value="stack"
                        class="px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60">
                        01_INTEL_STACK
                    </TabsTrigger>
                    <TabsTrigger value="brains"
                        class="px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60">
                        02_BRAIN_REGISTRY
                    </TabsTrigger>
                    <TabsTrigger value="general"
                        class="px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60">
                        03_CORE_IDENTITY
                    </TabsTrigger>
                </TabsList>
            </div>

            <!-- Intelligence Stack Tab -->
            <TabsContent value="stack" class="animate-in fade-in zoom-in-95 duration-500 outline-none">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    <div class="lg:col-span-2 space-y-10">
                        <!-- Health/Dependency Alert -->
                        <div v-if="activeBrain?.health?.status !== 'available'"
                            class="cyber-card border-amber-500/20 bg-amber-500/[0.02] p-8 flex items-start gap-6 animate-in slide-in-from-top-4 duration-700">
                            <div
                                class="p-3 rounded-2xl bg-amber-500/10 text-amber-500 shadow-[0_0_20px_rgba(245,158,11,0.2)]">
                                <AlertTriangle class="w-6 h-6" />
                            </div>
                            <div class="space-y-2 flex-1">
                                <h3 class="text-amber-500 font-black text-sm uppercase tracking-widest">Dependency
                                    Missing or Unreachable</h3>
                                <p class="text-white/40 text-xs font-medium leading-relaxed">
                                    {{ activeBrain?.health?.message || 'The configured LLM provider is not responding. Ensure Ollama or your cloud gateway is active.' }}
                                </p>
                                <div class="pt-2 flex gap-4">
                                    <a href="https://ollama.com/download" target="_blank"
                                        class="text-[9px] font-black text-amber-500/60 hover:text-amber-500 tracking-[0.2em] uppercase transition-colors">>>
                                        INSTALL_OLLAMA</a>
                                    <button @click="refreshAll"
                                        class="text-[9px] font-black text-white/20 hover:text-white transition-colors tracking-[0.2em] uppercase">>>
                                        RETRY_CONNECTION</button>
                                </div>
                            </div>
                        </div>

                        <!-- Inference Engine Configuration -->
                        <Card class="cyber-card p-10 space-y-10 border-ava-purple/20">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4">
                                    <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                        Neural Link Configuration</h2>
                                </div>
                                <div v-if="activeBrain"
                                    class="px-3 py-1 rounded-md bg-ava-purple/10 border border-ava-purple/20 text-[9px] font-black text-ava-purple uppercase tracking-widest">
                                    ACTIVE: {{ activeBrain.name }}
                                </div>
                            </div>

                            <div v-if="activeBrain?.config_schema?.length"
                                class="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-12">
                                <div v-for="field in activeBrain.config_schema" :key="field.name" class="space-y-4">
                                    <div class="flex justify-between items-end px-1">
                                        <Label
                                            class="text-[10px] font-black text-white/30 tracking-[0.2em] uppercase">{{
                                            field.name.replace('_', ' ') }}</Label>
                                        <span v-if="field.type !== 'string' && field.type !== 'bool'"
                                            class="text-ava-purple font-mono font-black text-sm tabular-nums">
                                            {{ brainConfigState[field.name] }}
                                        </span>
                                    </div>

                                    <!-- String/Input or Select for Model -->
                                    <template v-if="field.type === 'string'">
                                        <div
                                            v-if="field.name === 'model' && activeBrain?.health?.available_models?.length">
                                            <Select v-model="brainConfigState[field.name]"
                                                @update:modelValue="saveBrainConfig">
                                                <SelectTrigger
                                                    class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6 hover:bg-white/[0.04]">
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent
                                                    class="bg-[#0a0a0f] border-white/10 text-white rounded-xl">
                                                    <SelectItem v-for="m in activeBrain.health.available_models"
                                                        :key="m" :value="m">
                                                        {{ m }}
                                                    </SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <Input v-else v-model="brainConfigState[field.name]"
                                            class="bg-white/[0.02] border-white/5 text-white h-14 rounded-2xl px-6 focus:border-ava-purple/50 focus:bg-white/[0.04] transition-all font-mono text-sm"
                                            @change="saveBrainConfig" />
                                    </template>

                                    <!-- Float/Slider -->
                                    <Slider v-if="field.type === 'float'" v-model="brainSliderRefs[field.name]"
                                        :max="field.max || 1" :min="field.min || 0" :step="field.step || 0.01"
                                        class="py-2 spectral-slider"
                                        @update:modelValue="(val) => { brainConfigState[field.name] = val[0]; saveBrainConfig(); }" />

                                    <!-- Int/Slider -->
                                    <Slider v-if="field.type === 'int'" v-model="brainSliderRefs[field.name]"
                                        :max="field.max || 32768" :min="field.min || 256" :step="field.step || 128"
                                        class="py-2 spectral-slider"
                                        @update:modelValue="(val) => { brainConfigState[field.name] = val[0]; saveBrainConfig(); }" />

                                    <!-- Bool/Switch -->
                                    <div v-if="field.type === 'bool'"
                                        class="flex items-center justify-between h-14 bg-white/[0.02] border border-white/5 rounded-2xl px-6">
                                        <span
                                            class="text-[9px] font-black text-white/20 uppercase tracking-widest">ENABLED</span>
                                        <Switch :checked="brainConfigState[field.name]"
                                            @update:checked="(val) => { brainConfigState[field.name] = val; saveBrainConfig(); }" />
                                    </div>

                                    <p
                                        class="text-[9px] text-white/10 font-bold uppercase tracking-widest leading-tight px-1 italic">
                                        {{ field.description
                                        }}</p>
                                </div>
                            </div>
                            <div v-else
                                class="flex flex-col items-center justify-center py-20 text-center space-y-4 opacity-20 border border-dashed border-white/10 rounded-3xl">
                                <Pentagon class="w-12 h-12 text-white" />
                                <p class="text-[10px] font-black uppercase tracking-[0.3em]">Neural stack
                                    self-optimizing...</p>
                            </div>
                        </Card>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                            <Card class="cyber-card p-10 space-y-10 group">
                                <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4">
                                    <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                        Kernel Paths</h2>
                                </div>
                                <div class="space-y-8">
                                    <div class="space-y-3">
                                        <Label
                                            class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Model
                                            Repository</Label>
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
                                            class="text-[9px] font-black text-white/20 tracking-[0.2em] uppercase ml-1">Knowledge
                                            Vault
                                            (Vector DB)</Label>
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

                            <div
                                class="glass-panel p-10 rounded-3xl flex flex-col justify-center gap-6 border-white/[0.01]">
                                <div class="space-y-2">
                                    <div class="text-[9px] font-black text-[#34d399] tracking-widest uppercase">
                                        SYSLOG_TELEMETRY</div>
                                    <p
                                        class="text-[11px] text-white/30 font-bold leading-relaxed uppercase tracking-tighter">
                                        Your local
                                        intelligence stack is running on NVIDIA CUDA 12.4. Tensor cores are engaged for
                                        high-speed inference.
                                    </p>
                                </div>
                                <div class="flex gap-3">
                                    <div v-for="i in 12" :key="i"
                                        class="h-8 w-1.5 bg-white/[0.02] rounded-full overflow-hidden relative">
                                        <div class="absolute bottom-0 left-0 w-full bg-ava-purple rounded-full transition-all duration-1000"
                                            :style="{ height: Math.random() * 100 + '%', opacity: 0.2 + Math.random() * 0.5 }">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="space-y-10">
                        <!-- Telemetry Card -->
                        <Card class="cyber-card p-10 space-y-10 overflow-hidden relative border-ava-purple/20">
                            <div class="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
                                <Pentagon class="w-32 h-32 text-ava-purple rotate-12" />
                            </div>
                            <div class="flex justify-between items-center relative z-10">
                                <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                    Engine Pulse</h2>
                                <div class="flex items-center gap-2">
                                    <div
                                        class="w-1.5 h-1.5 bg-[#34d399] rounded-full neon-pulse shadow-[0_0_8px_#34d399]">
                                    </div>
                                    <span
                                        class="text-[9px] font-black text-[#34d399] tracking-widest uppercase">LIVE_STATS</span>
                                </div>
                            </div>

                            <div class="space-y-10 relative z-10">
                                <div v-if="activeBrain?.health" class="space-y-4">
                                    <div
                                        class="flex justify-between items-center text-[10px] font-black tracking-widest uppercase">
                                        <span class="text-white/30 italic">Endpoint Status</span>
                                        <span
                                            :class="activeBrain.health.status === 'available' ? 'text-[#34d399]' : 'text-amber-500'"
                                            class="tabular-nums uppercase">{{ activeBrain.health.status }}</span>
                                    </div>
                                    <div class="flex items-center gap-3">
                                        <div class="flex-1 h-1 bg-white/[0.03] rounded-full overflow-hidden">
                                            <div class="h-full bg-ava-purple transition-all duration-1000"
                                                :style="{ width: activeBrain.health.status === 'available' ? '100%' : '30%' }">
                                            </div>
                                        </div>
                                        <span class="text-[8px] text-white/20 font-mono">{{
                                            activeBrain.health.latency_ms ?
                                            activeBrain.health.latency_ms.toFixed(0) + 'ms' : '---' }}</span>
                                    </div>
                                </div>

                                <div class="space-y-4">
                                    <div
                                        class="flex justify-between items-center text-[10px] font-black tracking-widest uppercase">
                                        <span class="text-white/30 italic">NPU Core Load</span>
                                        <span class="text-ava-purple tabular-nums">{{ intStats.npu_acceleration
                                            }}%</span>
                                    </div>
                                    <div
                                        class="h-1.5 w-full bg-white/[0.03] rounded-full overflow-hidden p-[1px] border border-white/[0.05]">
                                        <div class="h-full bg-gradient-to-r from-ava-purple to-[#9333ea] rounded-full shadow-[0_0_15px_rgba(124,58,237,0.5)] transition-all duration-1000"
                                            :style="{ width: intStats.npu_acceleration + '%' }"></div>
                                    </div>
                                </div>

                                <div class="space-y-4">
                                    <div
                                        class="flex justify-between items-center text-[10px] font-black tracking-widest uppercase">
                                        <span class="text-white/30 italic">Neural VRAM Affinity</span>
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
                                            TOKEN_VELOCITY</div>
                                        <div class="text-3xl font-black text-white tracking-tighter tabular-nums">{{
                                            intStats.tokens_sec
                                            }}<span class="text-xs text-white/20 ml-1 italic">/s</span></div>
                                    </div>
                                    <div
                                        class="glass-panel p-6 rounded-3xl text-center space-y-2 border-white/[0.01] hover:bg-white/[0.03] transition-all">
                                        <div class="text-[8px] font-black text-white/10 tracking-[0.2em] uppercase">
                                            LINK_LATENCY</div>
                                        <div class="text-3xl font-black text-white tracking-tighter tabular-nums">{{
                                            intStats.latency
                                            }}<span class="text-xs text-white/20 ml-1 italic">ms</span></div>
                                    </div>
                                </div>
                            </div>
                        </Card>

                        <div class="space-y-4">
                            <Button
                                class="w-full h-16 rounded-[2rem] bg-ava-purple hover:bg-[#6d28d9] text-white font-black text-[10px] tracking-[0.25em] uppercase shadow-[0_15px_40px_rgba(124,58,237,0.2)] gap-4 transition-all hover:scale-[1.02]">
                                <Database class="w-4 h-4" />
                                OPTIMIZE_LOCAL_WEIGHTS
                            </Button>
                            <Button variant="outline"
                                class="w-full h-16 rounded-[2rem] border-white/5 bg-white/[0.02] text-white/30 hover:bg-white/[0.05] hover:text-white font-black text-[10px] tracking-[0.25em] uppercase gap-4 transition-all">
                                <Download class="w-4 h-4" />
                                SYNC_NEURAL_MODELS
                            </Button>
                        </div>
                    </div>
                </div>
            </TabsContent>

            <!-- Brain Registry Tab -->
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
                                                :class="brain.health?.status === 'available' ? 'text-[#34d399]' : 'text-amber-500'">{{
                                                    brain.health?.status?.toUpperCase() || 'UNKNOWN' }}</span></span>
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
                    </div>
                </div>
            </TabsContent>

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
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                        </Card>
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
            <div class="hover:text-white/40 transition-colors cursor-help italic">AVA_INTEL_SYSTEM_V2.5.0-STABLE.ARC_64
            </div>
        </div>
    </div>
</template>

<script setup>
import {
    RefreshCw, Folder, Settings, Cpu,
    ShieldCheck, Database, Download, Brain,
    Pentagon, HardDrive, AlertTriangle
} from 'lucide-vue-next'

const { $ava } = useNuxtApp()

const activeTab = ref('stack')

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

// Computed Helpers
const activeBrain = computed(() => brains.value.find(b => b.id === activeBrainId.value))

// Dynamic Brain Config Reactive State
const brainConfigState = reactive({})
const brainSliderRefs = reactive({})

// Initialize Brain Config state when active brain changes
watch(activeBrain, (newBrain) => {
    if (newBrain && newBrain.config_data) {
        Object.entries(newBrain.config_data).forEach(([key, val]) => {
            brainConfigState[key] = val
            // Also update slider refs (Slider expects Array)
            const schemaField = newBrain.config_schema?.find(f => f.name === key)
            if (schemaField && (schemaField.type === 'float' || schemaField.type === 'int')) {
                brainSliderRefs[key] = [val]
            }
        })
    }
}, { immediate: true, deep: true })

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
const modelPath = ref('/home/ghost/.local/share/ava/models/llama3-8b.gguf')
const dbPath = ref('/var/lib/ava/chromadb/knowledge_base_01')

// Sync local refs when config loads
watch(configValue, (newVal) => {
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

const saveBrainConfig = () => {
    if (activeBrainId.value) {
        $ava.updateBrainConfig(activeBrainId.value, { ...brainConfigState })
    }
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
