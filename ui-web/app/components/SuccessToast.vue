<template>
  <div class="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-3 w-[360px] max-w-[90vw]">
    <div v-for="toast in $ava?.state?.successToasts || []" :key="toast.id"
      class="rounded-2xl border border-emerald-500/40 bg-black/80 backdrop-blur-lg shadow-2xl px-5 py-4 text-white/90">
      <div class="flex items-center justify-between gap-4">
        <div class="text-[12px] font-black tracking-[0.2em] uppercase text-emerald-400">
          Saved
        </div>
        <div class="text-[14px] text-white/80">
          {{ toast.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { $ava } = useNuxtApp()
</script>
