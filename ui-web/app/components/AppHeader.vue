<template>
  <header
    class="h-16 border-b border-white/[0.05] flex items-center justify-between px-8 bg-[#07070a] sticky top-0 z-50 transition-all font-sans">
    <div class="flex items-center gap-8">
      <div class="flex items-center gap-3">
        <div class="w-6 h-6 bg-[#7c3aed] rounded flex items-center justify-center shadow-[0_0_10px_#7c3aed44]">
          <span class="text-white font-black text-xs">⬢</span>
        </div>
        <div class="flex flex-col">
          <span class="text-xs font-black text-white tracking-[0.1em] uppercase">AVA COMMAND CENTER</span>
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-[#34d399] shadow-[0_0_8px_#34d399aa]"></div>
            <span class="text-[9px] font-bold text-white/40 tracking-widest uppercase">LOCAL-FIRST LLM ACTIVE</span>
          </div>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2 pr-4 border-r border-white/5">
        <Button variant="ghost" size="icon" class="h-8 w-8 text-white/40 hover:text-white hover:bg-white/5 rounded-lg">
          <Settings :size="16" stroke-width="2.5" />
        </Button>
        <Button variant="ghost" size="icon" class="h-8 w-8 text-white/40 hover:text-white hover:bg-white/5 rounded-lg">
          <Maximize2 :size="16" stroke-width="2.5" />
        </Button>
        <Button variant="ghost" size="icon"
          class="h-8 w-8 text-white/40 hover:text-ava-purple hover:bg-white/5 rounded-lg">
          <X :size="16" stroke-width="3" />
        </Button>
      </div>

      <div class="flex items-center gap-3 pl-2">
        <div
          class="h-8 w-8 rounded-lg bg-[#1a1a2e] border border-white/5 flex items-center justify-center font-black text-[10px] text-white/80 shadow-lg overflow-hidden">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Ghost" class="w-full h-full object-cover"
            alt="User" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Settings, Maximize2, X } from 'lucide-vue-next'
const { $ava } = useNuxtApp()
</script>
