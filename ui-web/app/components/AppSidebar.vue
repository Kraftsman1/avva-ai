<template>
  <aside class="w-80 h-screen cyber-panel flex flex-col pt-10 font-sans bg-[#000000] border-r border-white/[0.03] relative overflow-hidden z-[30]">
    <!-- Ambient gradient overlay -->
    <div class="absolute inset-0 bg-gradient-to-b from-ava-purple/[0.02] via-transparent to-transparent pointer-events-none"></div>

    <!-- System Pulse -->
    <div class="px-8 mb-12 relative z-10">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-2">
          <div class="w-1 h-1 rounded-full bg-ava-purple shadow-[0_0_8px_#7c3aed] animate-pulse"></div>
          <h2 class="text-[10px] font-black text-white/20 tracking-[0.3em] uppercase">TELEMETRY_PULSE</h2>
        </div>
        <div class="h-[1px] w-8 bg-gradient-to-r from-white/10 to-transparent"></div>
      </div>
      <div class="space-y-8">
        <div v-for="(val, label) in statsMap" :key="label" class="space-y-3 group cursor-help">
          <div
            class="flex justify-between text-[9px] font-black tracking-[0.1em] px-0.5 transition-colors">
            <span class="text-white/30 uppercase group-hover:text-white/60 transition-colors">{{ label }}</span>
            <span class="text-ava-purple font-mono tabular-nums group-hover:text-ava-purple/80 transition-colors">{{ formatStat(val, label) }}</span>
          </div>
          <div class="h-[3px] w-full bg-white/[0.02] rounded-full overflow-hidden border border-white/[0.02] group-hover:border-ava-purple/20 transition-colors relative">
            <!-- Shimmer effect on hover -->
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000"></div>
            <div
              class="h-full bg-gradient-to-r from-ava-purple to-[#9333ea] shadow-[0_0_10px_rgba(124,58,237,0.4)] transition-all duration-1000 relative z-10"
              :style="{ width: getPercent(val, label) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="px-6 flex-1 relative z-10">
      <div class="flex items-center gap-3 mb-6 px-2">
        <div class="h-[1px] w-6 bg-gradient-to-r from-ava-purple/50 to-transparent"></div>
        <h2 class="text-[10px] font-black text-white/30 tracking-[0.2em] uppercase">NAVIGATION</h2>
        <div class="flex-1 h-[1px] bg-gradient-to-r from-transparent to-white/5"></div>
      </div>
      <nav class="space-y-1.5">
        <Button v-for="item in navItems" :key="item.label" :variant="isItemActive(item) ? 'default' : 'ghost'"
          class="w-full justify-start gap-4 h-12 px-4 rounded-xl transition-all relative group overflow-hidden" :class="[
            isItemActive(item)
              ? 'bg-gradient-to-r from-[#7c3aed] to-[#9333ea] text-white hover:from-[#6d28d9] hover:to-[#7e22ce] shadow-[0_4px_15px_#7c3aed33]'
              : 'text-white/40 hover:text-white hover:bg-white/[0.03]',
          ]" @click="navigateToItem(item)">
          <!-- Shimmer effect for active item -->
          <div v-if="isItemActive(item)" class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></div>
          <!-- Hover scan line for inactive items -->
          <div v-else class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></div>

          <component :is="item.icon" :size="18" class="transition-transform group-hover:scale-110 relative z-10" stroke-width="2.5" />
          <span class="font-bold text-xs tracking-tight relative z-10">{{ item.label }}</span>
        </Button>
      </nav>
    </div>

    <!-- Section 3: Current Model (Footer) -->
    <div class="p-6 relative z-10">
      <Card class="bg-[#0c0c14] border-white/[0.05] rounded-xl p-4 shadow-xl relative overflow-hidden group hover:border-ava-purple/20 transition-all">
        <!-- Decorative corner accents -->
        <div class="absolute top-0 left-0 w-12 h-[1px] bg-gradient-to-r from-ava-purple/50 to-transparent"></div>
        <div class="absolute top-0 left-0 w-[1px] h-12 bg-gradient-to-b from-ava-purple/50 to-transparent"></div>

        <!-- Hover glow -->
        <div class="absolute inset-0 bg-gradient-to-br from-ava-purple/[0.03] via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

        <div class="flex flex-col gap-1 relative z-10">
          <span class="text-[9px] font-black text-white/30 tracking-[0.2em] uppercase">CURRENT MODEL</span>
          <span class="text-sm font-bold text-white tracking-tight">{{ activeModelName }}</span>
          <div class="flex items-center justify-between mt-2">
            <div class="flex items-center gap-1.5">
              <div class="relative">
                <div class="w-1.5 h-1.5 bg-[#34d399] rounded-full shadow-[0_0_8px_#34d399]"></div>
                <div class="absolute inset-0 w-1.5 h-1.5 bg-[#34d399] rounded-full animate-ping"></div>
              </div>
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
