<template>
  <div
    class="absolute bottom-12 left-1/2 -translate-x-1/2 w-full max-w-5xl px-10 animate-in fade-in slide-in-from-bottom-8 duration-1000">
    <div
      class="bg-black/80 border border-white/[0.05] p-2 shadow-[0_30px_60px_rgba(0,0,0,0.5)] rounded-[2rem] flex items-center gap-4 focus-within:border-ava-purple/30 focus-within:shadow-[0_0_30px_rgba(124,58,237,0.1)] transition-all group backdrop-blur-2xl">
      <!-- Left Utility Icons -->
      <div class="flex items-center gap-1 ml-3">
        <Button variant="ghost" size="icon"
          class="h-11 w-11 text-white/10 hover:text-white hover:bg-white/5 rounded-2xl transition-all">
          <Terminal :size="20" stroke-width="2.5" />
        </Button>
        <Button variant="ghost" size="icon"
          class="h-11 w-11 text-white/10 hover:text-white hover:bg-white/5 rounded-2xl transition-all">
          <Search :size="20" stroke-width="2.5" />
        </Button>
      </div>

      <div class="h-6 w-[1px] bg-white/[0.03] mx-1"></div>

      <input v-model="input" @keyup.enter="handleSend" type="text" placeholder="Query Neural Kernel..."
        class="flex-1 bg-transparent border-none outline-none text-[16px] font-medium placeholder:text-white/10 py-5 tracking-tight text-white/90 selection:bg-ava-purple/30" />

      <div class="flex items-center gap-5 mr-1">
        <div
          class="hidden md:flex items-center px-4 py-2 bg-white/[0.02] border border-white/[0.05] rounded-xl text-[9px] font-black text-white/10 tracking-[0.25em] uppercase">
          CMD + L
        </div>

        <Button
          variant="ghost"
          size="icon"
          class="h-11 w-11 rounded-2xl transition-all border border-transparent"
          :class="isRecording ? 'text-ava-purple border-ava-purple/40 bg-ava-purple/10' : 'text-white/20 hover:text-white hover:bg-white/5'"
          @pointerdown="startVoice"
          @pointerup="stopVoice"
          @pointerleave="stopVoice"
        >
          <Mic :size="20" stroke-width="2.5" />
        </Button>

        <Button @click="handleSend" size="icon"
          class="h-13 w-13 bg-gradient-to-br from-ava-purple to-[#9333ea] hover:scale-105 text-white rounded-[1.5rem] transition-all active:scale-95 shadow-[0_10px_30px_rgba(124,58,237,0.3)] disabled:opacity-5 disabled:scale-100"
          :disabled="!input.trim()">
          <ArrowUp :size="24" stroke-width="3" />
        </Button>
      </div>
    </div>

    <!-- Status Badges -->
    <div class="flex justify-center gap-12 mt-8 animate-in fade-in duration-1000 delay-500">
      <div v-for="badge in badges" :key="badge.label"
        class="flex items-center gap-3 opacity-20 hover:opacity-100 transition-all cursor-help group">
        <div class="p-1 rounded-sm bg-white/5 group-hover:bg-ava-purple/10 transition-colors">
          <component :is="badge.icon" :size="10" class="text-white group-hover:text-ava-purple transition-colors" />
        </div>
        <span
          class="text-[9px] font-black tracking-[0.3em] uppercase text-white/60 group-hover:text-white transition-colors">
          {{ badge.label }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Terminal, Search, Maximize2, ArrowUp, Zap, Shield, Database, Mic } from 'lucide-vue-next'

const { $ava } = useNuxtApp()
const input = ref('')
const isRecording = ref(false)
const assistantState = computed(() => $ava?.state?.assistantState)

const badges = [
  { icon: Zap, label: 'K_LATENCY: 12ms' },
  { icon: Shield, label: 'L_ENCRYPT_VAULT' },
  { icon: Database, label: 'RAG_CORE: STABLE' },
]

watch(assistantState, (state) => {
  if (state !== 'listening') {
    isRecording.value = false
  }
})

const handleSend = () => {
  if (input.value.trim()) {
    $ava?.sendCommand?.(input.value)
    input.value = ''
  }
}

const startVoice = () => {
  if (isRecording.value) return
  isRecording.value = true
  $ava?.startVoiceCapture?.()
}

const stopVoice = () => {
  isRecording.value = false
}
</script>
