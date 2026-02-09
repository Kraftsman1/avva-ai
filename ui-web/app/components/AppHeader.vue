<template>
  <header
    class="h-20 border-b border-white/[0.03] grid grid-cols-3 items-center px-8 bg-[#000000]/95 sticky top-0 z-[40] transition-all font-sans backdrop-blur-md relative overflow-hidden">
    <!-- Subtle gradient line at bottom -->
    <div class="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-ava-purple/10 to-transparent"></div>

    <!-- Left: Logo -->
    <div class="flex items-center gap-8">
      <NuxtLink to="/" class="flex items-center gap-4 hover:opacity-80 transition-all group">
        <div
          class="relative w-8 h-8 bg-gradient-to-br from-[#7127e9] to-[#9333ea] rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(124,58,237,0.3)] overflow-hidden">
          <!-- Scan line effect -->
          <div class="absolute inset-0 bg-gradient-to-b from-transparent via-white/20 to-transparent translate-y-[-100%] group-hover:translate-y-[100%] transition-transform duration-1000"></div>
          <span class="text-white font-black text-xs tracking-tighter relative z-10">AV</span>
        </div>
        <div class="flex flex-col">
          <span class="text-[10px] font-black text-white tracking-[0.25em] uppercase leading-none mb-1">AVA CORE
            SYSTEMS</span>
          <div class="flex items-center gap-2">
            <div class="relative">
              <div class="w-1.5 h-1.5 rounded-full bg-[#34d399] shadow-[0_0_8px_#34d399aa]"></div>
              <div class="absolute inset-0 w-1.5 h-1.5 rounded-full bg-[#34d399] animate-ping"></div>
            </div>
            <span class="text-[8px] font-black text-white/20 tracking-[0.2em] uppercase">NEURAL_KERNEL_ACTIVE</span>
          </div>
        </div>
      </NuxtLink>
    </div>

    <!-- Center: Status Indicator -->
    <div class="flex items-center justify-center">
      <div
        class="flex items-center gap-3 bg-black/80 px-5 py-2.5 rounded-full border transition-all duration-300 backdrop-blur-md relative overflow-hidden shadow-lg"
        :class="[
          assistantState !== 'idle' ? 'border-white/[0.2] shadow-[0_0_20px_rgba(0,0,0,0.4)]' : 'border-white/[0.08]',
          assistantState === 'thinking' ? 'shadow-[0_0_25px_rgba(251,191,36,0.3)]' : '',
          assistantState === 'listening' ? 'shadow-[0_0_25px_rgba(239,68,68,0.3)]' : '',
          assistantState === 'speaking' ? 'shadow-[0_0_25px_rgba(52,211,153,0.3)]' : ''
        ]">
        <!-- Ambient glow for active states -->
        <div v-if="assistantState !== 'idle'" class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.05] to-transparent animate-[scan_2s_ease-in-out_infinite]"></div>

        <div class="relative flex h-3 w-3 z-10">
          <span v-if="assistantState !== 'idle'"
            class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="statusColor"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 shadow-[0_0_10px]" :class="[statusColor, assistantState !== 'idle' ? 'shadow-current' : '']"></span>
        </div>
        <span class="text-[11px] font-black tracking-[0.25em] uppercase transition-colors duration-300 z-10"
          :class="statusTextColor">
          {{ assistantState }}
        </span>
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center justify-end gap-6">
      <div class="flex items-center gap-2 border-r border-white/[0.03] pr-6">
        <Button variant="ghost" size="icon" @click="$emit('toggle-history')" class="h-8 w-8 text-white/40 hover:text-ava-purple hover:bg-white/5 rounded-lg transition-all group" title="Conversation History">
          <Clock :size="16" stroke-width="2.5" class="group-hover:scale-110 transition-transform" />
        </Button>
        <Button variant="ghost" size="icon" class="h-8 w-8 text-white/40 hover:text-white hover:bg-white/5 rounded-lg transition-all group">
          <Settings :size="16" stroke-width="2.5" class="group-hover:rotate-45 transition-transform duration-500" />
        </Button>
        <Button variant="ghost" size="icon" class="h-8 w-8 text-white/40 hover:text-white hover:bg-white/5 rounded-lg transition-all group">
          <Maximize2 :size="16" stroke-width="2.5" class="group-hover:scale-110 transition-transform" />
        </Button>
        <Button variant="ghost" size="icon"
          class="h-8 w-8 text-white/40 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all group">
          <X :size="16" stroke-width="3" class="group-hover:rotate-90 transition-transform duration-300" />
        </Button>
      </div>

      <div class="flex items-center gap-3 pl-2">
        <div
          class="relative h-8 w-8 rounded-lg bg-[#1a1a2e] border border-white/5 flex items-center justify-center font-black text-[10px] text-white/80 shadow-lg overflow-hidden group cursor-pointer hover:border-ava-purple/30 transition-all">
          <!-- Scan line on hover -->
          <div class="absolute inset-0 bg-gradient-to-b from-transparent via-ava-purple/20 to-transparent translate-y-[-100%] group-hover:translate-y-[100%] transition-transform duration-1000"></div>
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Ghost" class="w-full h-full object-cover relative z-10"
            alt="User" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Settings, Maximize2, X, Clock } from 'lucide-vue-next'
defineEmits(['toggle-history'])
const { $ava } = useNuxtApp()

const assistantState = computed(() => $ava?.state?.assistantState || 'idle')

const statusColor = computed(() => {
  switch (assistantState.value) {
    case 'listening': return 'bg-red-500'
    case 'thinking': return 'bg-amber-400'
    case 'speaking': return 'bg-emerald-400'
    default: return 'bg-slate-500' // idle
  }
})

const statusTextColor = computed(() => {
  switch (assistantState.value) {
    case 'listening': return 'text-red-500'
    case 'thinking': return 'text-amber-400'
    case 'speaking': return 'text-emerald-400'
    default: return 'text-slate-500' // idle
  }
})
</script>

<style scoped>
@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>
