<template>
  <header
    class="h-20 border-b border-white/[0.03] flex items-center justify-between px-8 bg-[#000000] sticky top-0 z-50 transition-all font-sans backdrop-blur-md">
    <div class="flex items-center gap-8">
      <NuxtLink to="/" class="flex items-center gap-4 hover:opacity-80 transition-opacity">
        <div
          class="w-8 h-8 bg-gradient-to-br from-[#7127e9] to-[#9333ea] rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(124,58,237,0.3)]">
          <span class="text-white font-black text-xs tracking-tighter">AV</span>
        </div>
        <div class="flex flex-col">
          <span class="text-[10px] font-black text-white tracking-[0.25em] uppercase leading-none mb-1">AVA CORE
            SYSTEMS</span>
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-[#34d399] shadow-[0_0_8px_#34d399aa] animate-pulse"></div>
            <span class="text-[8px] font-black text-white/20 tracking-[0.2em] uppercase">NEURAL_KERNEL_ACTIVE</span>
          </div>
        </div>
      </NuxtLink>
    </div>

    <div class="flex items-center gap-6">
      <div class="flex items-center gap-2 border-r border-white/[0.03] pr-6">
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
