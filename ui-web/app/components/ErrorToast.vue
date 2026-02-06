<template>
  <div class="fixed top-6 right-6 z-50 flex flex-col gap-3 w-[360px] max-w-[90vw]">
    <div v-for="toast in $ava?.state?.errorToasts || []" :key="toast.id"
      class="rounded-2xl border border-ava-purple/30 bg-black/80 backdrop-blur-lg shadow-2xl px-5 py-4 text-white/90">
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="text-[11px] font-black tracking-[0.2em] uppercase text-ava-purple/70">
            {{ toast.code }}
          </div>
          <div class="text-[14px] mt-2 leading-relaxed text-white/90">
            {{ toast.message }}
          </div>
          <div class="text-[10px] mt-2 text-white/40 uppercase tracking-[0.2em]">
            {{ toast.severity }} • {{ formatTimestamp(toast.timestamp) }}
          </div>
        </div>
        <button
          class="text-white/40 hover:text-white transition-colors text-sm"
          @click="$ava?.dismissErrorToast(toast.id)"
          aria-label="Dismiss error"
        >
          ✕
        </button>
      </div>
      <div class="mt-3 flex gap-2" v-if="toast.retry_allowed">
        <button
          class="px-3 py-1.5 rounded-full text-[11px] font-black uppercase tracking-[0.2em] bg-ava-purple/20 text-ava-purple hover:bg-ava-purple/30 transition-colors"
          @click="$ava?.retryError(toast)"
        >
          Retry
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
