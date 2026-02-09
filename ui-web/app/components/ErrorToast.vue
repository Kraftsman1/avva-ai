<template>
  <div class="fixed top-6 right-6 z-50 flex flex-col gap-3 w-[360px] max-w-[90vw]">
    <div v-for="toast in $ava?.state?.errorToasts || []" :key="toast.id"
      class="rounded-2xl border border-ava-purple/30 bg-black/90 backdrop-blur-lg shadow-[0_20px_50px_rgba(124,58,237,0.2)] px-5 py-4 text-white/90 relative overflow-hidden animate-in slide-in-from-right-4 fade-in duration-500 group">
      <!-- Decorative corner accents -->
      <div class="absolute top-0 right-0 w-16 h-[1px] bg-gradient-to-l from-ava-purple/50 to-transparent"></div>
      <div class="absolute top-0 right-0 w-[1px] h-16 bg-gradient-to-b from-ava-purple/50 to-transparent"></div>

      <!-- Subtle pulse effect -->
      <div class="absolute inset-0 bg-gradient-to-r from-ava-purple/[0.03] via-transparent to-ava-purple/[0.03] animate-pulse pointer-events-none"></div>

      <div class="flex items-start justify-between gap-4 relative z-10">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-1 h-1 rounded-full bg-ava-purple shadow-[0_0_8px_#7c3aed] animate-pulse"></div>
            <div class="text-[11px] font-black tracking-[0.2em] uppercase text-ava-purple/70">
              {{ toast.code }}
            </div>
          </div>
          <div class="text-[14px] mt-2 leading-relaxed text-white/90">
            {{ toast.message }}
          </div>
          <div class="text-[10px] mt-2 text-white/40 uppercase tracking-[0.2em]">
            {{ toast.severity }} • {{ formatTimestamp(toast.timestamp) }}
          </div>
        </div>
        <button
          class="text-white/40 hover:text-red-400 transition-all text-sm w-6 h-6 flex items-center justify-center rounded-lg hover:bg-red-500/10 shrink-0 group/close"
          @click="$ava?.dismissErrorToast(toast.id)"
          aria-label="Dismiss error"
        >
          <span class="group-hover/close:rotate-90 transition-transform duration-300">✕</span>
        </button>
      </div>
      <div class="mt-3 flex gap-2 relative z-10" v-if="toast.retry_allowed">
        <button
          class="relative px-3 py-1.5 rounded-full text-[11px] font-black uppercase tracking-[0.2em] bg-ava-purple/20 text-ava-purple hover:bg-ava-purple/30 transition-all overflow-hidden group/retry"
          @click="$ava?.retryError(toast)"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/20 to-transparent translate-x-[-200%] group-hover/retry:translate-x-[200%] transition-transform duration-500"></div>
          <span class="relative z-10">Retry</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const { $ava } = useNuxtApp()

const formatTimestamp = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString()
}
</script>
