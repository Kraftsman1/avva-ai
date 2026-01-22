<template>
  <div class="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6">
    <div
      class="glass-card p-2 pr-4 shadow-cyber-strong flex items-center gap-4 focus-within:border-ava-purple/50 transition-all duration-300">
      <div class="flex items-center gap-1.5 ml-2">
        <span v-for="icon in ['⌨', '🔍', '👁']" :key="icon"
          class="text-sm text-ava-text-muted cursor-pointer hover:text-white p-1 hover:bg-white/5 rounded transition-all">
          {{ icon }}
        </span>
      </div>

      <input v-model="input" @keyup.enter="handleSend" type="text"
        placeholder="Request system diagnostics or ask AVA anything..."
        class="flex-1 bg-transparent border-none outline-none text-[15px] font-medium placeholder:text-ava-text-muted/50 py-3" />

      <div class="flex items-center gap-4">
        <span
          class="text-[9px] font-black text-ava-text-muted bg-ava-bg px-2 py-1 rounded-md border border-white/5 tracking-widest hidden sm:inline">CTRL
          + ENTER</span>

        <button @click="handleSend"
          class="w-10 h-10 bg-ava-purple-700 hover:bg-ava-purple-600 rounded-xl flex items-center justify-center text-white transition-all active:scale-95 shadow-lg disabled:opacity-50"
          :disabled="!input.trim()">
          <ArrowUp :size="20" stroke-width="3" />
        </button>
      </div>
    </div>

    <div class="flex justify-center gap-6 mt-4 animate-in fade-in slide-in-from-bottom-2">
      <div v-for="badge in badges" :key="badge.label"
        class="flex items-center gap-2 opacity-40 hover:opacity-80 transition-opacity cursor-help">
        <span class="text-xs">{{ badge.icon }}</span>
        <span class="text-[9px] font-black tracking-widest uppercase">{{ badge.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowUp } from 'lucide-vue-next'
const { $ava } = useNuxtApp()

const input = ref('')
const badges = [
  { icon: '⚡', label: 'LOW LATENCY BRAIN' },
  { icon: '🛡', label: 'ENCRYPTED LOCAL BRIDGE' },
  { icon: '📚', label: 'RAG CONTEXT: ENABLED' },
]

const handleSend = () => {
  if (input.value.trim()) {
    $ava?.sendCommand?.(input.value)
    input.value = ''
  }
}
</script>
