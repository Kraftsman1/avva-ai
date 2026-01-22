<template>
  <div class="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-4xl px-10">
    <div
      class="bg-[#0c0c14] border border-white/[0.05] p-3 shadow-2xl rounded-2xl flex items-center gap-4 focus-within:border-[#7c3aed44] transition-all group">
      <!-- Left Utility Icons -->
      <div class="flex items-center gap-1.5 ml-2">
        <Button variant="ghost" size="icon"
          class="h-9 w-9 text-white/20 hover:text-white hover:bg-white/5 rounded-xl transition-all">
          <Terminal :size="18" stroke-width="2.5" />
        </Button>
        <Button variant="ghost" size="icon"
          class="h-9 w-9 text-white/20 hover:text-white hover:bg-white/5 rounded-xl transition-all">
          <Search :size="18" stroke-width="2.5" />
        </Button>
        <Button variant="ghost" size="icon"
          class="h-9 w-9 text-white/20 hover:text-white hover:bg-white/5 rounded-xl transition-all">
          <Maximize2 :size="18" stroke-width="2.5" />
        </Button>
      </div>

      <div class="h-8 w-[1px] bg-white/5 mx-2"></div>

      <input v-model="input" @keyup.enter="handleSend" type="text" placeholder="Ask AVA or run a system command..."
        class="flex-1 bg-transparent border-none outline-none text-[15px] font-bold placeholder:text-white/10 py-3 tracking-tight text-white/90" />

      <div class="flex items-center gap-4 ml-2">
        <div
          class="hidden sm:flex items-center px-2.5 py-1.5 bg-[#07070a] border border-white/5 rounded-lg text-[9px] font-black text-white/30 tracking-[0.2em] uppercase">
          CTRL + ENTER
        </div>

        <Button @click="handleSend" size="icon"
          class="h-11 w-11 bg-gradient-to-br from-[#7c3aed] to-[#6d28d9] hover:from-[#8b5cf6] hover:to-[#7c3aed] text-white rounded-xl transition-all active:scale-95 shadow-[0_4px_15px_#7c3aed44] disabled:opacity-20"
          :disabled="!input.trim()">
          <ArrowUp :size="22" stroke-width="3" />
        </Button>
      </div>
    </div>

    <!-- Status Badges -->
    <div class="flex justify-center gap-10 mt-6 animate-in fade-in slide-in-from-bottom-2 duration-700">
      <div v-for="badge in badges" :key="badge.label"
        class="flex items-center gap-2.5 opacity-30 hover:opacity-100 transition-all cursor-help group">
        <component :is="badge.icon" :size="12" class="text-white group-hover:text-[#7c3aed] transition-colors" />
        <span
          class="text-[9px] font-black tracking-[0.2em] uppercase text-white/80 group-hover:text-white transition-colors">
          {{ badge.label }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Terminal, Search, Maximize2, ArrowUp, Zap, Shield, Database } from 'lucide-vue-next'

const { $ava } = useNuxtApp()
const input = ref('')

const badges = [
  { icon: Zap, label: 'LOW LATENCY MODE' },
  { icon: Shield, label: 'ENCRYPTED LOCAL STORAGE' },
  { icon: Database, label: 'RAG: DESKTOP DOCS' },
]

const handleSend = () => {
  if (input.value.trim()) {
    $ava?.sendCommand?.(input.value)
    input.value = ''
  }
}
</script>
