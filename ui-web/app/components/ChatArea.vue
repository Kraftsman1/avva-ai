<template>
  <div class="flex-1 flex flex-col p-8 pb-32 overflow-y-auto" ref="scrollContainer">
    <!-- Session Start Indicator -->
    <div class="flex justify-center mb-12">
      <div class="px-6 py-2 bg-ava-bg-elevated border border-ava-border rounded-full shadow-cyber">
        <span class="text-[10px] font-black tracking-[0.2em] text-ava-text-muted uppercase">SYSTEM PROTOCOL INITIALIZED: SESSION {{ sessionId }}</span>
      </div>
    </div>

    <!-- Messages -->
    <div class="max-w-4xl mx-auto w-full space-y-8">
      <div 
        v-for="msg in $ava.state.messages" 
        :key="msg.id"
        class="flex flex-col"
        :class="msg.sender === 'user' ? 'items-end' : 'items-start'"
      >
        <div 
          class="max-w-[80%] rounded-2xl p-5 shadow-lg border"
          :class="msg.sender === 'user' 
            ? 'bg-ava-purple-700 border-ava-purple-600 text-white rounded-tr-none' 
            : 'bg-ava-bg-elevated border-white/5 text-ava-text rounded-tl-none'"
        >
          <div v-if="msg.sender === 'avva'" class="flex items-center gap-2 mb-2 opacity-50">
            <span class="text-[9px] font-black tracking-widest uppercase">ENCRYPTED RESPONSE // 0x{{ msg.id.toString(16).slice(-4) }}</span>
          </div>
          
          <p class="text-[15px] leading-relaxed font-medium whitespace-pre-wrap">{{ msg.text }}</p>

          <!-- Structured Data Support (Stats, Apps, etc.) -->
          <div v-if="msg.data" class="mt-4 pt-4 border-t border-white/5 space-y-3">
             <div v-if="msg.data.type === 'system_stats'" class="grid grid-cols-3 gap-4">
                <div v-for="(v, k) in {CPU: msg.data.cpu, RAM: msg.data.ram, DISK: msg.data.disk}" :key="k" class="bg-black/20 p-3 rounded-xl border border-white/5">
                  <span class="block text-[10px] font-bold text-ava-text-muted mb-1">{{ k }}</span>
                  <span class="text-xl font-black text-ava-neon tracking-tight">{{ v }}%</span>
                </div>
             </div>
             
             <div v-if="msg.data.app" class="flex items-center gap-4 bg-black/20 p-3 rounded-xl border border-white/5">
                <div class="w-10 h-10 bg-ava-purple/20 flex items-center justify-center rounded-lg text-ava-purple font-black">
                  {{ msg.data.app[0].toUpperCase() }}
                </div>
                <div class="flex-1">
                  <span class="block text-xs font-bold text-white uppercase">{{ msg.data.app }}</span>
                  <span class="block text-[10px] text-ava-text-muted">EXECUTABLE // SYSTEM_ACCESS</span>
                </div>
                <button class="px-4 py-1.5 bg-ava-neon/20 text-ava-neon text-[10px] font-black rounded-full border border-ava-neon/30 hover:bg-ava-neon/40 transition-all uppercase">
                  Launch
                </button>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { $ava } = useNuxtApp()
const scrollContainer = ref(null)
const sessionId = ref(Math.floor(Math.random() * 9000) + 1000)

watch(() => $ava.state.messages.length, () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
})
</script>
