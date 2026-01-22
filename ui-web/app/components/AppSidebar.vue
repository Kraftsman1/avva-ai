<template>
  <aside class="w-80 h-screen cyber-panel flex flex-col pt-10 font-sans bg-[#000000] border-r border-white/[0.03]">
    <!-- Section 1: System Pulse -->
    <div class="px-8 mb-12">
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-[10px] font-black text-white/20 tracking-[0.3em] uppercase">TELEMETRY_PULSE</h2>
        <div class="h-[1px] w-8 bg-white/5"></div>
      </div>
      <div class="space-y-8">
        <div v-for="(val, label) in statsMap" :key="label" class="space-y-3 group">
          <div
            class="flex justify-between text-[9px] font-black tracking-[0.1em] px-0.5 transition-colors group-hover:text-white">
            <span class="text-white/30 uppercase group-hover:text-white/60 transition-colors">{{ label }}</span>
            <span class="text-ava-purple font-mono tabular-nums">{{ formatStat(val, label) }}</span>
          </div>
          <div class="h-[3px] w-full bg-white/[0.02] rounded-full overflow-hidden border border-white/[0.02]">
            <div
              class="h-full bg-gradient-to-r from-ava-purple to-[#9333ea] shadow-[0_0_10px_rgba(124,58,237,0.4)] transition-all duration-1000"
              :style="{ width: getPercent(val, label) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 2: Navigation -->
    <div class="px-6 flex-1">
      <h2 class="text-[10px] font-black text-white/30 tracking-[0.2em] uppercase mb-4 px-2">NAVIGATION</h2>
      <nav class="space-y-1.5">
        <Button v-for="item in navItems" :key="item.label" :variant="isItemActive(item) ? 'default' : 'ghost'"
          class="w-full justify-start gap-4 h-12 px-4 rounded-xl transition-all relative group overflow-hidden" :class="[
            isItemActive(item)
              ? 'bg-[#7c3aed] text-white hover:bg-[#6d28d9] shadow-[0_4px_15px_#7c3aed33]'
              : 'text-white/40 hover:text-white hover:bg-white/[0.03]',
          ]" @click="navigateToItem(item)">
          <component :is="item.icon" :size="18" class="transition-transform group-hover:scale-110" stroke-width="2.5" />
          <span class="font-bold text-xs tracking-tight">{{ item.label }}</span>
        </Button>
      </nav>
    </div>

    <!-- Section 3: Current Model (Footer) -->
    <div class="p-6">
      <Card class="bg-[#0c0c14] border-white/[0.05] rounded-xl p-4 shadow-xl">
        <div class="flex flex-col gap-1">
          <span class="text-[9px] font-black text-white/30 tracking-[0.2em] uppercase">CURRENT MODEL</span>
          <span class="text-sm font-bold text-white tracking-tight">{{ activeModelName }}</span>
          <div class="flex items-center justify-between mt-2">
            <div class="flex items-center gap-1.5">
              <div class="w-1.5 h-1.5 bg-[#34d399] rounded-full"></div>
              <span class="text-[9px] font-bold text-[#34d399] tracking-widest uppercase">STABLE</span>
            </div>
            <span class="text-[9px] font-bold text-white/20 font-mono tracking-tighter">V1.2.4-STABLE</span>
          </div>
        </div>
      </Card>
    </div>
  </aside>
</template>

<script setup>
import { MessageSquare, Brain, HardDrive, Terminal } from 'lucide-vue-next'

const { $ava } = useNuxtApp()

const navItems = [
  { label: 'Active Chat', icon: MessageSquare, path: '/' },
  { label: 'Intelligence Stack', icon: Brain, path: '/settings' },
  { label: 'Local Files', icon: HardDrive, path: '#' },
  { label: 'Kernel Logs', icon: Terminal, path: '#' },
]

const route = useRoute()
const isItemActive = (item) => route.path === item.path

const navigateToItem = (item) => {
  if (item.path !== '#') {
    navigateTo(item.path)
  }
}

const stats = computed(() => $ava?.state?.systemStats || { cpu: 0, ram: 0, vram: 0 })
const activeModelName = computed(() => $ava?.state?.activeModel || 'Llama-3-8B-Instruct')

const statsMap = computed(() => ({
  'CPU Usage': stats.value.cpu,
  'GPU VRAM': stats.value.vram,
  'System RAM': stats.value.ram,
}))

const formatStat = (val, label) => {
  if (label === 'GPU VRAM') {
    if (stats.value.vram_total) {
      const used = (stats.value.vram_used / 1024).toFixed(1)
      const total = (stats.value.vram_total / 1024).toFixed(1)
      return `${used} / ${total}GB`
    }
    return `${val.toFixed(1)}%`
  }
  if (label === 'System RAM') return `${val.toFixed(1)}%`
  return `${val.toFixed(0)}%`
}

const getPercent = (val, label) => {
  return val
}
</script>

<style scoped>
/* No extra styles needed, fully Tailwind + main.css */
</style>
