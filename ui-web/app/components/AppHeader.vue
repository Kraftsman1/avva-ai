<template>
  <header class="h-20 border-b border-ava-border flex items-center justify-between px-10 bg-ava-bg/50 backdrop-blur-md sticky top-0 z-50">
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/5 rounded-full">
        <div 
          class="w-2 h-2 rounded-full animate-pulse shadow-[0_0_8px]"
          :class="$ava.state.isConnected ? 'bg-ava-neon shadow-ava-neon/50' : 'bg-red-500 shadow-red-500/50'"
        ></div>
        <span class="text-[10px] font-black tracking-widest text-ava-text-muted uppercase">
          {{ $ava.state.isConnected ? 'AVA LOCAL BRIDGE ACTIVE' : 'RECONNECTING...' }}
        </span>
      </div>
      
      <div class="h-4 w-[1px] bg-white/10 mx-2"></div>
      
      <span class="text-xs font-bold text-ava-purple tracking-widest uppercase">
        {{ $ava.state.assistantState }}
      </span>
    </div>

    <div class="flex items-center gap-6">
      <button class="text-ava-text-muted hover:text-white transition-colors">
        <Bell :size="20" />
      </button>
      <div class="h-8 w-8 rounded-full bg-ava-purple-700 flex items-center justify-center font-black text-xs text-white border-2 border-ava-bg shadow-cyber">
        SK
      </div>
    </div>
  </header>
</template>

<script setup>
import { Bell } from 'lucide-vue-next'
const { $ava } = useNuxtApp()
</script>
