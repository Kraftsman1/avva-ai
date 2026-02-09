<template>
  <div class="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-3 w-[360px] max-w-[90vw]">
    <div v-for="toast in $ava?.state?.successToasts || []" :key="toast.id"
      class="rounded-2xl border border-emerald-500/40 bg-black/90 backdrop-blur-lg shadow-[0_20px_50px_rgba(16,185,129,0.2)] px-5 py-4 text-white/90 relative overflow-hidden animate-in slide-in-from-top-4 fade-in duration-500 group">
      <!-- Decorative corner accents -->
      <div class="absolute top-0 left-0 w-16 h-[1px] bg-gradient-to-r from-emerald-500/50 to-transparent"></div>
      <div class="absolute top-0 left-0 w-[1px] h-16 bg-gradient-to-b from-emerald-500/50 to-transparent"></div>
      <div class="absolute bottom-0 right-0 w-16 h-[1px] bg-gradient-to-l from-emerald-500/50 to-transparent"></div>
      <div class="absolute bottom-0 right-0 w-[1px] h-16 bg-gradient-to-t from-emerald-500/50 to-transparent"></div>

      <!-- Subtle glow effect -->
      <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/[0.03] via-transparent to-emerald-500/[0.03] animate-pulse pointer-events-none"></div>

      <div class="flex items-center gap-4 relative z-10">
        <div class="flex items-center gap-2">
          <div class="relative">
            <div class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]"></div>
            <div class="absolute inset-0 w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
          </div>
          <div class="text-[12px] font-black tracking-[0.2em] uppercase text-emerald-400">
            Saved
          </div>
        </div>
        <div class="text-[14px] text-white/80">
          {{ toast.message }}
        </div>
      </div>

      <!-- Animated progress bar at bottom -->
      <div class="absolute bottom-0 left-0 right-0 h-[2px] bg-emerald-500/20 overflow-hidden">
        <div class="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 animate-[shrink_2s_linear_forwards] shadow-[0_0_8px_#34d399]"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shrink {
  from { width: 100%; }
  to { width: 0%; }
}
</style>

<script setup>
const { $ava } = useNuxtApp()
</script>
