<template>
  <ScrollArea class="flex-1 h-full bg-transparent" ref="scrollContainer">
    <div class="flex-1 flex flex-col p-10 pb-40 max-w-5xl mx-auto w-full font-sans">
      <!-- Session Start Indicator -->
      <div class="flex justify-center mb-20 px-10 animate-in fade-in slide-in-from-top-4 duration-1000">
        <div
          class="px-8 py-3 bg-white/[0.02] border border-white/[0.04] rounded-2xl flex items-center gap-4 shadow-2xl backdrop-blur-md">
          <div class="w-1.5 h-1.5 bg-ava-purple rounded-full shadow-[0_0_10px_#7c3aed]"></div>
          <span class="text-[10px] font-black text-white/30 tracking-[0.3em] uppercase">
            {{ currentSessionLabel }}
          </span>
        </div>
      </div>

      <!-- Messages -->
      <div class="space-y-12">
        <div v-for="(msg, idx) in $ava?.state?.messages || []" :key="msg.id"
          class="flex flex-col animate-in fade-in slide-in-from-bottom-8 duration-700"
          :class="msg.sender === 'user' ? 'items-end' : 'items-start'" :style="{ animationDelay: (idx * 50) + 'ms' }">

          <!-- Message Group -->
          <div class="max-w-[88%] lg:max-w-[80%] flex items-start gap-6"
            :class="msg.sender === 'user' ? 'flex-row-reverse' : ''">

            <!-- Icon for AVA -->
            <div v-if="msg.sender !== 'user'"
              class="w-12 h-12 rounded-2xl bg-black border border-ava-purple/20 flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.1)] shrink-0 mt-1 relative overflow-hidden group">
              <div
                class="absolute inset-0 bg-gradient-to-br from-ava-purple/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              </div>
              <Bot :size="24" class="text-ava-purple relative z-10" />
            </div>

            <div class="flex flex-col" :class="msg.sender === 'user' ? 'items-end' : 'items-start'">
              <!-- Attribution -->
              <span class="text-[9px] font-black tracking-[0.25em] uppercase mb-3 px-1"
                :class="msg.sender === 'user' ? 'text-white/20' : 'text-ava-purple/50'">
                {{ msg.sender === 'user' ? 'USER_INPUT' : 'AVA_CORE_RESPONSE' }}
              </span>

              <!-- Content Bubble -->
              <div
                class="p-4 rounded-[2.5rem] transition-all duration-500 hover:shadow-[0_20px_50px_rgba(0,0,0,0.3)] border border-transparent"
                :class="msg.sender === 'user'
                  ? 'bubble-user rounded-tr-none'
                  : 'bubble-ava rounded-tl-none border-white/[0.02]'
                  ">
                <div v-if="hasCode(msg.text)">
                  <p class="text-[16px] leading-[1.6] mb-6 font-medium tracking-tight text-white/90">{{
                    getTextBeforeCode(msg.text) }}</p>
                  <div class="bg-black rounded-3xl border border-white/[0.04] overflow-hidden shadow-2xl my-4">
                    <div
                      class="px-6 py-4 bg-white/[0.02] border-b border-white/[0.04] flex justify-between items-center">
                      <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-white/10"></div>
                        <span
                          class="text-[10px] font-black text-white/30 tracking-[0.2em] uppercase">neural_script.sh</span>
                      </div>
                      <Copy :size="14" class="text-white/20 hover:text-white cursor-pointer transition-colors" />
                    </div>
                    <pre
                      class="p-8 font-mono text-sm overflow-x-auto text-ava-purple/80 selection:bg-ava-purple/30"><code>{{ getCode(msg.text) }}</code></pre>
                  </div>
                  <p v-if="getTextAfterCode(msg.text)"
                    class="text-[16px] leading-[1.6] mt-6 font-medium tracking-tight text-white/90">
                    {{ getTextAfterCode(msg.text) }}
                  </p>
                </div>
                <p v-else class="text-[16px] leading-[1.6] font-medium tracking-tight text-white/90">
                  {{ msg.text }}
                </p>

                <!-- System Telemetry Overlay in Chat -->
                <div v-if="msg.text.includes('temperature') || msg.text.includes('thermal')"
                  class="mt-6 pt-6 border-t border-white/[0.05] flex flex-wrap gap-6 animate-in fade-in duration-1000">
                  <div class="flex items-center gap-3">
                    <div class="w-1.5 h-1.5 rounded-full bg-ava-purple shadow-[0_0_8px_#7c3aed]"></div>
                    <span class="text-[9px] font-black text-white/30 uppercase tracking-[0.2em]">NODE_TEMP: 54°C</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-1.5 h-1.5 rounded-full bg-red-500/50"></div>
                    <span class="text-[9px] font-black text-white/30 uppercase tracking-[0.2em]">THRESHOLD: 85°C</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- User Avatar -->
            <div v-if="msg.sender === 'user'"
              class="w-12 h-12 rounded-2xl bg-black border border-white/5 flex items-center justify-center shadow-lg shrink-0 mt-1 overflow-hidden group">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Ghost"
                class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" alt="You" />
            </div>
          </div>
        </div>
      </div>

      <!-- Thinking Indicator Bubble -->
      <div v-if="isThinking" class="flex flex-col items-start animate-in fade-in duration-300 mt-12 pl-10">
        <div class="max-w-[88%] lg:max-w-[80%] flex items-start gap-6">
          <!-- Icon for AVA -->
          <div
            class="w-12 h-12 rounded-2xl bg-black border border-ava-purple/20 flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.1)] shrink-0 mt-1">
            <Bot :size="24" class="text-ava-purple animate-pulse" />
          </div>

          <div class="flex flex-col items-start">
            <!-- Attribution -->
            <span class="text-[9px] font-black tracking-[0.25em] uppercase mb-3 px-1 text-ava-purple/50 animate-pulse">
              NEURAL_PROCESSING
            </span>
            <!-- Content Bubble -->
            <div
              class="p-4 rounded-[2.5rem] rounded-tl-none border border-white/[0.02] bubble-ava flex items-center gap-3">
              <div class="w-1.5 h-1.5 bg-ava-purple rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div class="w-1.5 h-1.5 bg-ava-purple rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div class="w-1.5 h-1.5 bg-ava-purple rounded-full animate-bounce"></div>
              <!-- Stop Button -->
              <button
                @click="interrupt"
                class="ml-2 px-4 py-1.5 bg-red-500/20 border border-red-500/40 rounded-full text-[10px] font-black text-red-400 hover:bg-red-500/30 transition-colors tracking-[0.15em]">
                STOP
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Speaking Indicator with Stop -->
      <div v-if="isSpeaking" class="flex flex-col items-start animate-in fade-in duration-300 mt-12 pl-10">
        <div class="max-w-[88%] lg:max-w-[80%] flex items-start gap-6">
          <div
            class="w-12 h-12 rounded-2xl bg-black border border-ava-purple/20 flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.1)] shrink-0 mt-1">
            <Bot :size="24" class="text-ava-purple" />
          </div>
          <div class="flex flex-col items-start">
            <span class="text-[9px] font-black tracking-[0.25em] uppercase mb-3 px-1 text-ava-purple/50">
              AVA_RESPONSE
            </span>
            <div class="p-4 rounded-[2.5rem] rounded-tl-none border border-white/[0.02] bubble-ava flex items-center gap-3">
              <span class="text-[14px] font-medium text-white/70 italic">Speaking...</span>
              <button
                @click="interrupt"
                class="ml-2 px-4 py-1.5 bg-red-500/20 border border-red-500/40 rounded-full text-[10px] font-black text-red-400 hover:bg-red-500/30 transition-colors tracking-[0.15em]">
                STOP
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </ScrollArea>
</template>

<script setup>
import { Bot, Copy } from 'lucide-vue-next'

const { $ava } = useNuxtApp()
const scrollContainer = ref(null)

const isThinking = computed(() => $ava?.state?.assistantState === 'thinking')
const isSpeaking = computed(() => $ava?.state?.assistantState === 'speaking')
const currentSessionLabel = computed(() => {
  const title = $ava?.state?.currentConversationTitle || 'New Conversation'
  return title.toUpperCase().replace(/[^A-Z0-9\s]/g, '').replace(/\s+/g, '_')
})

const interrupt = () => {
  if ($ava?.ws?.readyState === WebSocket.OPEN) {
    $ava.ws.send(JSON.stringify({
      id: crypto.randomUUID(),
      type: 'assistant.interrupt',
      payload: {}
    }))
  }
}

// Auto-scroll when thinking state changes
watch(isThinking, (newVal) => {
  if (newVal) {
    nextTick(() => {
      const viewport = scrollContainer.value?.$el?.querySelector('[data-radix-scroll-area-viewport]')
      if (viewport) {
        viewport.scrollTo({
          top: viewport.scrollHeight,
          behavior: 'smooth'
        })
      }
    })
  }
})

const hasCode = (text) => text.includes('```')
const getCode = (text) => text.split('```')[1]?.split('\n').slice(1).join('\n')
const getTextBeforeCode = (text) => text.split('```')[0]
const getTextAfterCode = (text) => text.split('```')[2]

watch(
  () => $ava?.state?.messages?.length,
  () => {
    nextTick(() => {
      const viewport = scrollContainer.value?.$el?.querySelector('[data-radix-scroll-area-viewport]')
      if (viewport) {
        viewport.scrollTo({
          top: viewport.scrollHeight,
          behavior: 'smooth'
        })
      }
    })
  }
)
</script>

<style scoped>
.bubble-user {
  @apply selection:bg-white/20;
}

.bubble-ava {
  @apply selection:bg-ava-purple/30;
}
</style>
