<template>
    <div class="h-full w-full overflow-y-auto p-6 lg:p-14 font-sans bg-[#000000] selection:bg-ava-purple/30 relative">
        <!-- Ambient background gradients -->
        <div class="fixed inset-0 pointer-events-none overflow-hidden">
            <div class="absolute top-0 left-1/4 w-[600px] h-[600px] bg-ava-purple/[0.03] rounded-full blur-[120px] animate-pulse"></div>
            <div class="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-[#9333ea]/[0.02] rounded-full blur-[100px] animate-pulse" style="animation-delay: 1s;"></div>
        </div>

        <!-- Breadcrumbs & Meta -->
        <div class="flex items-center justify-between mb-10 animate-in fade-in slide-in-from-top-4 duration-700 relative">
            <div class="flex items-center gap-2 text-[10px] font-black text-white/20 tracking-[0.2em] uppercase">
                <NuxtLink to="/" class="hover:text-ava-purple transition-colors relative group">
                    <span class="relative z-10">OS_LAYER</span>
                    <div class="absolute inset-0 bg-ava-purple/10 rounded opacity-0 group-hover:opacity-100 transition-opacity blur"></div>
                </NuxtLink>
                <span class="opacity-30">/</span>
                <span class="text-white/40">INTEL_STACK_CORE</span>
            </div>
            <div class="flex items-center gap-3">
                <div class="h-[1px] w-12 bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
                <span class="text-[9px] font-mono text-white/10 tracking-widest">LAYER_VISUALIZER_STABLE</span>
            </div>
        </div>

        <!-- Header Section -->
        <div
            class="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-16 animate-in fade-in slide-in-from-left-4 duration-700 delay-100 relative">
            <div class="space-y-4">
                <div class="flex items-center gap-4">
                    <div
                        class="relative w-12 h-12 rounded-2xl bg-gradient-to-br from-ava-purple to-[#9333ea] flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.3)] overflow-hidden group">
                        <!-- Scan line effect -->
                        <div class="absolute inset-0 bg-gradient-to-b from-transparent via-white/20 to-transparent translate-y-[-100%] group-hover:translate-y-[100%] transition-transform duration-1000"></div>
                        <Cpu class="w-6 h-6 text-white relative z-10" />
                    </div>
                    <h1 class="text-5xl font-black text-white tracking-tighter italic relative">
                        Intelligence Stack
                        <div class="absolute -bottom-2 left-0 w-24 h-[2px] bg-gradient-to-r from-ava-purple via-ava-purple/50 to-transparent"></div>
                    </h1>
                </div>
                <p class="text-white/30 font-medium text-lg max-w-xl leading-relaxed">
                    Tuning the neural kernel and hardware acceleration for optimal local-first response.
                </p>
            </div>
            <div class="flex gap-4">
                <Button variant="outline"
                    class="relative border-white/5 bg-white/[0.02] text-white/40 hover:bg-white/[0.05] hover:text-white hover:border-ava-purple/30 gap-3 font-black text-[10px] tracking-[0.2em] uppercase px-8 h-14 rounded-2xl group transition-all overflow-hidden"
                    @click="refreshAll"
                    :disabled="isSaving">
                    <!-- Shimmer effect -->
                    <div class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></div>
                    <RefreshCw class="w-4 h-4 group-hover:rotate-180 transition-transform duration-700 relative z-10" />
                    <span class="relative z-10">RECALIBRATE</span>
                </Button>
            </div>
        </div>

        <div class="mb-8 flex items-center justify-between relative">
            <div v-if="isSaving" class="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.2em] text-ava-purple/70 relative group">
                <div class="relative">
                    <div class="w-2 h-2 rounded-full bg-ava-purple animate-pulse"></div>
                    <div class="absolute inset-0 w-2 h-2 rounded-full bg-ava-purple animate-ping"></div>
                </div>
                <span>Saving changes...</span>
                <!-- Animated progress bar -->
                <div class="absolute -bottom-1.5 left-0 right-0 h-[1px] bg-white/5 overflow-hidden">
                    <div class="h-full w-1/3 bg-gradient-to-r from-transparent via-ava-purple to-transparent animate-[scan_1.5s_ease-in-out_infinite]"></div>
                </div>
            </div>
        </div>

        <Tabs v-model="activeTab" class="w-full relative" :class="{ 'opacity-70 pointer-events-none': isSaving }">
            <div
                class="flex items-center justify-between mb-12 border-b border-white/[0.03] pb-1 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200 relative">
                <!-- Subtle glow effect on active tab -->
                <div class="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-ava-purple/20 to-transparent pointer-events-none"></div>

                <TabsList class="bg-transparent p-0 gap-10 h-auto">
                    <TabsTrigger value="stack"
                        class="relative px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60 group">
                        <span class="relative z-10">01_INTEL_STACK</span>
                        <!-- Active glow -->
                        <div class="absolute bottom-0 left-0 right-0 h-[2px] bg-ava-purple opacity-0 data-[state=active]:opacity-100 shadow-[0_0_10px_#7c3aed] transition-opacity"></div>
                    </TabsTrigger>
                    <TabsTrigger value="brains"
                        class="relative px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60 group">
                        <span class="relative z-10">02_BRAIN_REGISTRY</span>
                        <div class="absolute bottom-0 left-0 right-0 h-[2px] bg-ava-purple opacity-0 data-[state=active]:opacity-100 shadow-[0_0_10px_#7c3aed] transition-opacity"></div>
                    </TabsTrigger>
                    <TabsTrigger value="general"
                        class="relative px-0 py-4 bg-transparent data-[state=active]:bg-transparent data-[state=active]:text-ava-purple text-white/20 font-black text-[11px] tracking-[0.3em] uppercase rounded-none border-b-2 border-transparent data-[state=active]:border-ava-purple transition-all hover:text-white/60 group">
                        <span class="relative z-10">03_CORE_IDENTITY</span>
                        <div class="absolute bottom-0 left-0 right-0 h-[2px] bg-ava-purple opacity-0 data-[state=active]:opacity-100 shadow-[0_0_10px_#7c3aed] transition-opacity"></div>
                    </TabsTrigger>
                </TabsList>
            </div>

            <!-- Intelligence Stack Tab -->
            <TabsContent value="stack" class="animate-in fade-in zoom-in-95 duration-500 outline-none">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    <div class="lg:col-span-2 space-y-10">
                        <!-- Health/Dependency Alert -->
                        <div v-if="activeBrain?.health?.status !== 'available'"
                            class="relative cyber-card border-amber-500/20 bg-amber-500/[0.02] p-8 flex items-start gap-6 animate-in slide-in-from-top-4 duration-700 overflow-hidden group">
                            <!-- Alert pulse effect -->
                            <div class="absolute inset-0 bg-gradient-to-r from-amber-500/[0.03] via-transparent to-amber-500/[0.03] animate-pulse"></div>

                            <div
                                class="relative p-3 rounded-2xl bg-amber-500/10 text-amber-500 shadow-[0_0_20px_rgba(245,158,11,0.2)]">
                                <AlertTriangle class="w-6 h-6 animate-pulse" />
                                <div class="absolute inset-0 rounded-2xl border border-amber-500/30 animate-ping"></div>
                            </div>
                            <div class="space-y-2 flex-1 relative z-10">
                                <h3 class="text-amber-500 font-black text-sm uppercase tracking-widest">Dependency
                                    Missing or Unreachable</h3>
                                <p class="text-white/40 text-xs font-medium leading-relaxed">
                                    {{ activeBrain?.health?.message || 'The configured LLM provider is not responding. Ensure Ollama or your cloud gateway is active.' }}
                                </p>
                                <div class="pt-2 flex gap-4">
                                    <a href="https://ollama.com/download" target="_blank"
                                        class="text-[9px] font-black text-amber-500/60 hover:text-amber-500 tracking-[0.2em] uppercase transition-colors hover:translate-x-1 inline-block">>>
                                        INSTALL_OLLAMA</a>
                                    <button @click="refreshAll"
                                        class="text-[9px] font-black text-white/20 hover:text-white transition-all tracking-[0.2em] uppercase hover:translate-x-1">>>
                                        RETRY_CONNECTION</button>
                                </div>
                            </div>
                        </div>

                        <!-- Inference Engine Configuration -->
                        <Card class="cyber-card p-10 space-y-10 border-ava-purple/20 relative overflow-hidden group">
                            <!-- Corner accents -->
                            <div class="absolute top-0 left-0 w-24 h-[1px] bg-gradient-to-r from-ava-purple/50 to-transparent"></div>
                            <div class="absolute top-0 left-0 w-[1px] h-24 bg-gradient-to-b from-ava-purple/50 to-transparent"></div>
                            <div class="absolute bottom-0 right-0 w-24 h-[1px] bg-gradient-to-l from-ava-purple/50 to-transparent"></div>
                            <div class="absolute bottom-0 right-0 w-[1px] h-24 bg-gradient-to-t from-ava-purple/50 to-transparent"></div>

                            <div class="flex items-center justify-between relative z-10">
                                <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4">
                                    <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                        Neural Link Configuration</h2>
                                </div>
                                <div v-if="activeBrain"
                                    class="px-3 py-1 rounded-md bg-ava-purple/10 border border-ava-purple/20 text-[9px] font-black text-ava-purple uppercase tracking-widest relative overflow-hidden group/badge">
                                    <div class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/10 to-transparent translate-x-[-200%] group-hover/badge:translate-x-[200%] transition-transform duration-700"></div>
                                    <span class="relative z-10">ACTIVE: {{ activeBrain.name }}</span>
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
                                                    <SelectValue
                                                        :placeholder="brainConfigState[field.name] || 'SELECT_MODEL'" />
                                                </SelectTrigger>
                                                <SelectContent
                                                    class="bg-[#0a0a0f] border-white/10 text-white rounded-xl">
                                                    <SelectItem
                                                        v-if="brainConfigState[field.name] && !activeBrain.health.available_models.includes(brainConfigState[field.name])"
                                                        :value="brainConfigState[field.name]" class="opacity-50 italic">
                                                        {{ brainConfigState[field.name] }} (Missing)
                                                    </SelectItem>
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
                            <Card class="cyber-card p-10 space-y-10 group relative overflow-hidden">
                                <!-- Hover effect -->
                                <div class="absolute inset-0 bg-gradient-to-br from-ava-purple/[0.02] via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                                <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4 relative z-10">
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
                                class="glass-panel p-10 rounded-3xl flex flex-col justify-center gap-6 border-white/[0.01] relative overflow-hidden group">
                                <!-- Scan line effect -->
                                <div class="absolute inset-0 bg-gradient-to-b from-transparent via-[#34d399]/[0.03] to-transparent translate-y-[-100%] group-hover:translate-y-[100%] transition-transform duration-2000"></div>

                                <div class="space-y-2 relative z-10">
                                    <div class="flex items-center gap-2">
                                        <div class="w-1 h-1 rounded-full bg-[#34d399] shadow-[0_0_8px_#34d399] animate-pulse"></div>
                                        <div class="text-[9px] font-black text-[#34d399] tracking-widest uppercase">
                                            SYSLOG_TELEMETRY</div>
                                    </div>
                                    <p
                                        class="text-[11px] text-white/30 font-bold leading-relaxed uppercase tracking-tighter">
                                        Your local
                                        intelligence stack is running on NVIDIA CUDA 12.4. Tensor cores are engaged for
                                        high-speed inference.
                                    </p>
                                </div>
                                <div class="flex gap-3 relative z-10">
                                    <div v-for="i in 12" :key="i"
                                        class="h-8 w-1.5 bg-white/[0.02] rounded-full overflow-hidden relative group/bar">
                                        <div class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-ava-purple to-[#34d399] rounded-full transition-all duration-1000 group-hover/bar:from-[#34d399] group-hover/bar:to-ava-purple"
                                            :style="{ height: Math.random() * 100 + '%', opacity: 0.2 + Math.random() * 0.5 }">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="space-y-10">
                        <!-- Telemetry Card -->
                        <Card class="cyber-card p-10 space-y-10 overflow-hidden relative border-ava-purple/20 group">
                            <!-- Animated background glow -->
                            <div class="absolute inset-0 bg-gradient-to-br from-ava-purple/[0.03] via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>

                            <div class="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none group-hover:opacity-[0.05] transition-opacity">
                                <Pentagon class="w-32 h-32 text-ava-purple rotate-12 group-hover:rotate-45 transition-transform duration-1000" />
                            </div>

                            <div class="flex justify-between items-center relative z-10">
                                <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                                    Engine Pulse</h2>
                                <div class="flex items-center gap-2 relative">
                                    <div class="relative">
                                        <div class="w-1.5 h-1.5 bg-[#34d399] rounded-full shadow-[0_0_8px_#34d399]"></div>
                                        <div class="absolute inset-0 w-1.5 h-1.5 bg-[#34d399] rounded-full animate-ping"></div>
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
                                class="relative w-full h-16 rounded-[2rem] bg-gradient-to-br from-ava-purple to-[#9333ea] hover:from-[#6d28d9] hover:to-[#7e22ce] text-white font-black text-[10px] tracking-[0.25em] uppercase shadow-[0_15px_40px_rgba(124,58,237,0.2)] gap-4 transition-all hover:scale-[1.02] overflow-hidden group">
                                <!-- Shimmer effect -->
                                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></div>
                                <Database class="w-4 h-4 relative z-10" />
                                <span class="relative z-10">OPTIMIZE_LOCAL_WEIGHTS</span>
                            </Button>
                            <Button variant="outline"
                                class="relative w-full h-16 rounded-[2rem] border-white/5 bg-white/[0.02] text-white/30 hover:bg-white/[0.05] hover:text-white hover:border-ava-purple/30 font-black text-[10px] tracking-[0.25em] uppercase gap-4 transition-all overflow-hidden group">
                                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/5 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></div>
                                <Download class="w-4 h-4 relative z-10" />
                                <span class="relative z-10">SYNC_NEURAL_MODELS</span>
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
                            class="cyber-card p-6 flex flex-col sm:flex-row items-center justify-between gap-6 group hover:translate-x-1 animate-in slide-in-from-right-4 duration-500 relative overflow-hidden"
                            :style="{ animationDelay: idx * 100 + 'ms' }">
                            <!-- Hover glow effect -->
                            <div class="absolute inset-0 bg-gradient-to-r from-ava-purple/[0.03] via-transparent to-ava-purple/[0.03] opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                            <div class="flex items-center gap-6 relative z-10">
                                <div
                                    class="relative w-16 h-16 rounded-[1.25rem] bg-white/[0.02] border border-white/[0.05] flex items-center justify-center text-ava-purple group-hover:scale-110 transition-transform duration-500 overflow-hidden">
                                    <!-- Scan line on hover -->
                                    <div class="absolute inset-0 bg-gradient-to-b from-transparent via-ava-purple/20 to-transparent translate-y-[-100%] group-hover:translate-y-[100%] transition-transform duration-1000"></div>

                                    <Brain v-if="brain.provider !== 'openai'" class="w-8 h-8 relative z-10" />
                                    <Pentagon v-else class="w-8 h-8 relative z-10" />

                                    <div v-if="activeBrainId === brain.id"
                                        class="absolute -top-1 -right-1 w-4 h-4 bg-ava-purple rounded-full border-2 border-[#000000] shadow-[0_0_10px_#7c3aed]">
                                        <div class="absolute inset-0 w-4 h-4 bg-ava-purple rounded-full animate-ping"></div>
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
                        <Card class="cyber-card p-10 space-y-10 relative overflow-hidden group">
                            <!-- Corner accents -->
                            <div class="absolute top-0 left-0 w-16 h-[1px] bg-gradient-to-r from-ava-purple/50 to-transparent"></div>
                            <div class="absolute top-0 left-0 w-[1px] h-16 bg-gradient-to-b from-ava-purple/50 to-transparent"></div>

                            <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4 relative z-10">
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
                    <Card class="cyber-card p-10 space-y-10 group relative overflow-hidden">
                        <!-- Decorative corners -->
                        <div class="absolute top-0 right-0 w-20 h-[1px] bg-gradient-to-l from-ava-purple/50 to-transparent"></div>
                        <div class="absolute top-0 right-0 w-[1px] h-20 bg-gradient-to-b from-ava-purple/50 to-transparent"></div>

                        <div class="flex items-center gap-4 border-l-2 border-ava-purple pl-4 relative z-10">
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
                        <Card class="cyber-card p-10 space-y-10 relative overflow-hidden group">
                            <!-- Ambient glow -->
                            <div class="absolute inset-0 bg-gradient-to-br from-[#34d399]/[0.02] via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>

                            <div class="flex items-center gap-4 border-l-2 border-[#34d399] pl-4 relative z-10">
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
                <Card class="cyber-card p-10 mt-10 relative overflow-hidden group">
                    <!-- Corner accents for error section -->
                    <div class="absolute top-0 left-0 w-24 h-[1px] bg-gradient-to-r from-red-500/30 to-transparent"></div>
                    <div class="absolute top-0 left-0 w-[1px] h-24 bg-gradient-to-b from-red-500/30 to-transparent"></div>

                    <div class="flex items-center gap-4 border-l-2 border-red-500/40 pl-4 relative z-10">
                        <h2 class="text-xl font-black text-white tracking-tight uppercase tracking-[0.1em]">
                            Error Log</h2>
                        <span class="text-[9px] font-black text-white/30 tracking-[0.2em] uppercase">
                            Last 50
                        </span>
                    </div>
                    <div class="mt-6 space-y-4 max-h-[320px] overflow-y-auto pr-2 relative z-10">
                        <div v-if="errorLog.length === 0"
                            class="text-[11px] font-black tracking-[0.2em] uppercase text-white/20 text-center py-10">
                            <div class="w-12 h-12 mx-auto mb-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center justify-center">
                                <span class="text-2xl">✓</span>
                            </div>
                            No errors recorded.
                        </div>
                        <div v-for="entry in errorLog" :key="entry.id"
                            class="flex items-start justify-between gap-6 border border-white/5 rounded-2xl px-5 py-4 bg-white/[0.02] hover:bg-white/[0.03] hover:border-red-500/20 transition-all group/error relative overflow-hidden">
                            <!-- Subtle error glow -->
                            <div class="absolute inset-0 bg-gradient-to-r from-red-500/[0.02] via-transparent to-red-500/[0.02] opacity-0 group-hover/error:opacity-100 transition-opacity"></div>

                            <div class="relative z-10">
                                <div class="text-[9px] font-black tracking-[0.2em] uppercase text-ava-purple/60">
                                    {{ entry.code }}
                                </div>
                                <div class="text-[13px] text-white/80 mt-2 leading-relaxed">
                                    {{ entry.message }}
                                </div>
                                <div class="text-[9px] mt-2 text-white/30 uppercase tracking-[0.2em]">
                                    {{ entry.severity }} • {{ new Date(entry.timestamp).toLocaleString() }}
                                </div>
                            </div>
                            <button v-if="entry.retry_allowed && entry.context?.command"
                                class="relative px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] bg-ava-purple/20 text-ava-purple hover:bg-ava-purple/30 transition-all overflow-hidden group/retry shrink-0"
                                @click="$ava?.sendCommand(entry.context.command)">
                                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/10 to-transparent translate-x-[-200%] group-hover/retry:translate-x-[200%] transition-transform duration-500"></div>
                                <span class="relative z-10">Retry</span>
                            </button>
                        </div>
                    </div>
                </Card>
            </TabsContent>
        </Tabs>

        <!-- Footer Stats -->
        <div
            class="mt-20 pt-10 border-t border-white/[0.03] flex flex-col md:flex-row justify-between items-center gap-6 text-[9px] font-black tracking-[0.3em] text-white/10 uppercase relative">
            <!-- Subtle gradient line above footer -->
            <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-ava-purple/10 to-transparent"></div>

            <div class="flex items-center gap-8">
                <div class="flex items-center gap-3 group cursor-help">
                    <div class="relative">
                        <div class="w-1.5 h-1.5 bg-[#34d399] rounded-full shadow-[0_0_8px_#34d39966]"></div>
                        <div class="absolute inset-0 w-1.5 h-1.5 bg-[#34d399] rounded-full animate-ping"></div>
                    </div>
                    <span class="group-hover:text-[#34d399] transition-colors">KERNEL: OLLAMA/v0.1.32</span>
                </div>
                <div class="opacity-50 hover:opacity-100 transition-opacity cursor-help">DRIVER: NVIDIA_CUDA_12.4.X</div>
            </div>
            <div class="hover:text-white/40 transition-colors cursor-help italic relative group">
                <span>AVA_INTEL_SYSTEM_V2.5.0-STABLE.ARC_64</span>
                <div class="absolute -bottom-0.5 left-0 right-0 h-[1px] bg-gradient-to-r from-ava-purple via-ava-purple to-ava-purple scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
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
const errorLog = computed(() => $ava?.state?.errorLog || [])
const pendingOps = computed(() => $ava?.state?.pendingOps || [])
const isSaving = computed(() => pendingOps.value.length > 0)

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
@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

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
