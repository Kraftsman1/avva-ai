<template>
  <aside class="bg-ava-bg-sidebar border-r border-ava-border flex flex-col p-6">
    <!-- Branding -->
    <div class="mb-10 flex items-center gap-3">
      <div class="text-3xl text-ava-purple font-black tracking-tighter shadow-ava-purple/20 shadow-xl">⬢</div>
      <div class="flex flex-col">
        <span class="text-va-text-bright font-black text-xs tracking-[0.2em]">AVA CORE</span>
        <span class="text-[10px] text-ava-text-muted font-bold tracking-widest">LINUX ENVIRONMENT</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 space-y-2">
      <button 
        v-for="item in navItems" 
        :key="item.label"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group"
        :class="item.active ? 'bg-ava-purple-700 shadow-cyber text-white' : 'text-ava-text-muted hover:bg-white/5 hover:text-white'"
      >
        <component :is="item.icon" :size="18" :class="item.active ? 'text-white' : 'text-ava-text-muted group-hover:text-white'" />
        <span class="font-bold text-sm tracking-tight">{{ item.label }}</span>
      </button>
    </nav>

    <!-- System Pulse -->
    <div class="mt-auto pt-10 border-t border-ava-border/50">
      <div class="flex items-center gap-2 mb-4 opacity-50">
        <span class="text-xs font-black tracking-widest">SYSTEM PULSE</span>
      </div>
      
      <div class="space-y-4">
        <div v-for="(val, label) in stats" :key="label" class="space-y-1.5">
          <div class="flex justify-between text-[11px] font-bold tracking-tight px-1">
            <span class="text-ava-text-muted uppercase">{{ label }}</span>
            <span class="text-ava-text-bright text-opacity-80">{{ val }}%</span>
          </div>
          <div class="h-1.5 w-full bg-ava-bg rounded-full overflow-hidden border border-white/5">
            <div 
              class="h-full bg-ava-purple transition-all duration-1000" 
              :style="{ width: val + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Hub -->
    <div class="mt-8">
      <div class="bg-ava-bg-elevated/40 border border-white/5 rounded-2xl p-4 flex flex-col gap-1">
        <span class="text-[10px] font-black text-ava-neon tracking-widest mb-1">STABLE BRAIN ACTIVE</span>
        <span class="text-sm font-bold text-white">{{ $ava.state.activeModel }}</span>
        <span class="text-[10px] text-ava-text-muted font-mono">v1.5.0-LOCAL-FP16</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { LayoutDashboard, MessageSquare, Shield, Brain, Settings } from 'lucide-vue-next'

const { $ava } = useNuxtApp()

const navItems = [
  { label: 'DASHBOARD', icon: LayoutDashboard, active: false },
  { label: 'CONVERSATIONS', icon: MessageSquare, active: true },
  { label: 'BRAIN HUB', icon: Brain, active: false },
  { label: 'SECURITY', icon: Shield, active: false },
  { label: 'SETTINGS', icon: Settings, active: false },
]

const stats = computed(() => $ava.state.systemStats)
</script>
