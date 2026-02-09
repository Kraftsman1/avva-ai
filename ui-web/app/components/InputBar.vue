<template>
  <div
    class="absolute bottom-12 left-1/2 -translate-x-1/2 w-full max-w-5xl px-10 animate-in fade-in slide-in-from-bottom-8 duration-1000 z-40">

    <!-- Main Input Container -->
    <div
      class="relative bg-gradient-to-br from-black/90 via-black/85 to-black/90 border shadow-[0_30px_80px_rgba(0,0,0,0.6)] rounded-[2.5rem] flex items-center gap-5 transition-all group backdrop-blur-2xl overflow-hidden"
      :class="[
        isFocused || input.trim()
          ? 'border-ava-purple/30 shadow-[0_0_40px_rgba(124,58,237,0.15),0_30px_80px_rgba(0,0,0,0.6)]'
          : 'border-white/[0.06]'
      ]">

      <!-- Ambient glow on focus -->
      <div
        class="absolute inset-0 bg-gradient-to-br from-ava-purple/[0.03] via-transparent to-transparent opacity-0 transition-opacity duration-500"
        :class="{ 'opacity-100': isFocused || input.trim() }"></div>

      <!-- Animated scan line -->
      <div
        v-if="isRecording"
        class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/10 to-transparent animate-[scan_2s_ease-in-out_infinite]"></div>

      <!-- Left Utility Icons -->
      <div class="flex items-center gap-2 ml-4 relative z-10">
        <Button
          variant="ghost"
          size="icon"
          class="h-11 w-11 text-white/15 hover:text-ava-purple hover:bg-ava-purple/10 rounded-2xl transition-all duration-300 group/icon">
          <Terminal :size="20" stroke-width="2.5" class="group-hover/icon:scale-110 transition-transform" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          class="h-11 w-11 text-white/15 hover:text-ava-purple hover:bg-ava-purple/10 rounded-2xl transition-all duration-300 group/icon">
          <Search :size="20" stroke-width="2.5" class="group-hover/icon:scale-110 transition-transform" />
        </Button>
      </div>

      <div class="h-8 w-[1px] bg-gradient-to-b from-transparent via-white/[0.06] to-transparent"></div>

      <!-- Input Field -->
      <div class="flex-1 relative z-10">
        <input
          v-model="input"
          @keyup.enter="handleSend"
          @focus="isFocused = true"
          @blur="isFocused = false"
          type="text"
          placeholder="Initialize neural query protocol..."
          class="w-full bg-transparent border-none outline-none text-[16px] font-medium placeholder:text-white/12 placeholder:tracking-wide py-6 tracking-tight text-white/90 selection:bg-ava-purple/30"
        />

        <!-- Character counter for long inputs -->
        <div
          v-if="input.length > 100"
          class="absolute right-0 bottom-1 text-[8px] font-black text-white/10 tracking-wider">
          {{ input.length }}_CHARS
        </div>
      </div>

      <!-- Right Action Icons -->
      <div class="flex items-center gap-4 mr-2 relative z-10">
        <!-- Keyboard Shortcut Hint -->
        <div
          class="hidden md:flex items-center gap-2 px-4 py-2.5 bg-white/[0.02] border border-white/[0.05] rounded-xl transition-all hover:border-white/[0.08]">
          <div class="flex items-center gap-1">
            <kbd class="text-[9px] font-black text-white/15 tracking-[0.2em]">⌘</kbd>
            <span class="text-[8px] text-white/10">+</span>
            <kbd class="text-[9px] font-black text-white/15 tracking-[0.2em]">L</kbd>
          </div>
        </div>

        <!-- Voice Input Button -->
        <Button
          variant="ghost"
          size="icon"
          class="relative h-12 w-12 rounded-2xl transition-all duration-300 border group/voice"
          :class="isRecording
            ? 'text-ava-purple border-ava-purple/50 bg-ava-purple/15 shadow-[0_0_20px_rgba(124,58,237,0.3)]'
            : 'text-white/25 border-transparent hover:text-white hover:bg-white/[0.05] hover:border-white/[0.08]'"
          @pointerdown="startVoice"
          @pointerup="stopVoice"
          @pointerleave="stopVoice"
        >
          <!-- Pulse ring when recording -->
          <div
            v-if="isRecording"
            class="absolute inset-0 rounded-2xl border-2 border-ava-purple/50 animate-ping"></div>

          <Mic :size="20" stroke-width="2.5" class="relative z-10 group-hover/voice:scale-110 transition-transform" />
        </Button>

        <!-- Send Button -->
        <Button
          @click="handleSend"
          size="icon"
          class="relative h-14 w-14 rounded-[1.8rem] transition-all duration-300 group/send overflow-hidden"
          :class="input.trim()
            ? 'bg-gradient-to-br from-ava-purple to-[#9333ea] hover:scale-105 active:scale-95 shadow-[0_10px_35px_rgba(124,58,237,0.35)] text-white'
            : 'bg-white/[0.03] text-white/10 cursor-not-allowed border border-white/[0.05]'"
          :disabled="!input.trim()">

          <!-- Shimmer effect when active -->
          <div
            v-if="input.trim()"
            class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-200%] group-hover/send:translate-x-[200%] transition-transform duration-700"></div>

          <ArrowUp :size="24" stroke-width="3" class="relative z-10 group-hover/send:translate-y-[-2px] transition-transform" />
        </Button>
      </div>
    </div>

    <!-- Status Badges -->
    <div class="flex justify-center gap-14 mt-9 animate-in fade-in duration-1000 delay-500">
      <div v-for="badge in badges" :key="badge.label"
        class="group/badge flex items-center gap-3 opacity-15 hover:opacity-100 transition-all duration-300 cursor-help">
        <div class="relative">
          <div class="p-1.5 rounded-lg bg-white/[0.03] group-hover/badge:bg-ava-purple/10 border border-white/[0.05] group-hover/badge:border-ava-purple/20 transition-all">
            <component :is="badge.icon" :size="10" class="text-white/60 group-hover/badge:text-ava-purple transition-colors" stroke-width="2.5" />
          </div>
          <!-- Active indicator -->
          <div class="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 bg-emerald-400 rounded-full opacity-0 group-hover/badge:opacity-100 transition-opacity shadow-[0_0_6px_#10b981]"></div>
        </div>
        <span
          class="text-[9px] font-black tracking-[0.28em] uppercase text-white/50 group-hover/badge:text-white transition-colors">
          {{ badge.label }}
        </span>
      </div>
    </div>

    <!-- Recording Indicator -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0 scale-95 translate-y-4"
      leave-active-class="transition-all duration-200"
      leave-to-class="opacity-0 scale-95 translate-y-4"
    >
      <div v-if="isRecording" class="absolute -top-20 left-1/2 -translate-x-1/2">
        <div class="px-6 py-3 bg-ava-purple/20 border border-ava-purple/40 rounded-2xl backdrop-blur-xl shadow-[0_10px_40px_rgba(124,58,237,0.3)]">
          <div class="flex items-center gap-3">
            <div class="relative">
              <div class="w-2 h-2 bg-ava-purple rounded-full animate-pulse"></div>
              <div class="absolute inset-0 w-2 h-2 bg-ava-purple rounded-full animate-ping"></div>
            </div>
            <span class="text-[10px] font-black text-ava-purple tracking-[0.22em] uppercase">
              Voice_Capture_Active
            </span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { Terminal, Search, ArrowUp, Zap, Shield, Database, Mic } from 'lucide-vue-next'

const { $ava } = useNuxtApp()
const input = ref('')
const isRecording = ref(false)
const isFocused = ref(false)
const assistantState = computed(() => $ava?.state?.assistantState)

const badges = [
  { icon: Zap, label: 'Latency_12ms' },
  { icon: Shield, label: 'Encrypted' },
  { icon: Database, label: 'Core_Stable' },
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
    isFocused.value = false
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

<style scoped>
@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>
