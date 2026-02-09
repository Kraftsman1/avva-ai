<template>
  <ScrollArea class="flex-1 h-full bg-transparent relative" ref="scrollContainer">
    <!-- Ambient background effects -->
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(124,58,237,0.03),transparent_50%)] pointer-events-none"></div>
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_80%_80%,rgba(124,58,237,0.02),transparent_40%)] pointer-events-none"></div>

    <div class="flex-1 flex flex-col p-10 pb-40 max-w-5xl mx-auto w-full font-sans relative">
      <!-- Session Start Indicator -->
      <div class="flex justify-center mb-24 px-10 animate-in fade-in slide-in-from-top-4 duration-1000">
        <div
          class="group px-10 py-4 bg-black/40 border border-white/[0.06] rounded-3xl flex items-center gap-5 shadow-[0_10px_40px_rgba(0,0,0,0.4)] backdrop-blur-xl relative overflow-hidden hover:border-ava-purple/20 transition-all duration-500">
          <!-- Animated gradient background -->
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-ava-purple/[0.03] to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000"></div>

          <div class="relative flex items-center gap-4">
            <div class="relative">
              <div class="w-2 h-2 bg-ava-purple rounded-full shadow-[0_0_12px_#7c3aed] animate-pulse"></div>
              <div class="absolute inset-0 w-2 h-2 bg-ava-purple rounded-full shadow-[0_0_12px_#7c3aed] animate-ping"></div>
            </div>
            <span class="text-[10px] font-black text-white/35 tracking-[0.32em] uppercase">
              Session_Active:
            </span>
            <span class="text-[11px] font-black text-ava-purple/70 tracking-[0.18em] uppercase">
              {{ currentSessionLabel }}
            </span>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div class="space-y-14">
        <div v-for="(msg, idx) in $ava?.state?.messages || []" :key="msg.id"
          class="flex flex-col animate-in fade-in slide-in-from-bottom-8 duration-700 group/message"
          :class="msg.sender === 'user' ? 'items-end' : 'items-start'"
          :style="{ animationDelay: (idx * 50) + 'ms' }">

          <!-- Message Group -->
          <div class="max-w-[90%] lg:max-w-[82%] flex items-start gap-7"
            :class="msg.sender === 'user' ? 'flex-row-reverse' : ''">

            <!-- Avatar for AVA -->
            <div v-if="msg.sender !== 'user'"
              class="w-14 h-14 rounded-2xl bg-gradient-to-br from-black via-black to-ava-purple/10 border border-ava-purple/25 flex items-center justify-center shadow-[0_0_25px_rgba(124,58,237,0.15)] shrink-0 mt-1 relative overflow-hidden group-hover/message:border-ava-purple/40 transition-all duration-500">
              <div
                class="absolute inset-0 bg-gradient-to-br from-ava-purple/10 via-transparent to-transparent opacity-0 group-hover/message:opacity-100 transition-opacity duration-700">
              </div>
              <!-- Scan line effect -->
              <div class="absolute inset-0 bg-gradient-to-b from-transparent via-ava-purple/10 to-transparent h-full translate-y-[-100%] group-hover/message:translate-y-[100%] transition-transform duration-1000"></div>
              <Bot :size="26" class="text-ava-purple relative z-10" stroke-width="2" />
            </div>

            <div class="flex flex-col flex-1" :class="msg.sender === 'user' ? 'items-end' : 'items-start'">
              <!-- Attribution with Timestamp -->
              <div class="flex items-center gap-3 mb-3.5 px-2">
                <div class="flex items-center gap-2">
                  <div class="w-1 h-1 rounded-full"
                    :class="msg.sender === 'user' ? 'bg-white/15' : 'bg-ava-purple/40'"></div>
                  <span class="text-[9px] font-black tracking-[0.26em] uppercase"
                    :class="msg.sender === 'user' ? 'text-white/25' : 'text-ava-purple/55'">
                    {{ msg.sender === 'user' ? 'User_Input' : 'Neural_Response' }}
                  </span>
                </div>
                <span v-if="msg.timestamp" class="text-[8px] font-bold text-white/15 tracking-wide">
                  {{ formatTimestamp(msg.timestamp) }}
                </span>
              </div>

              <!-- Content Bubble -->
              <div
                class="relative p-5 rounded-[2.2rem] transition-all duration-500 border group-hover/message:shadow-[0_20px_60px_rgba(0,0,0,0.4)]"
                :class="msg.sender === 'user'
                  ? 'bg-white/[0.04] border-white/[0.08] rounded-tr-lg backdrop-blur-sm hover:bg-white/[0.06] hover:border-white/[0.12]'
                  : 'bg-gradient-to-br from-black/60 via-black/50 to-ava-purple/[0.02] border-ava-purple/[0.08] rounded-tl-lg backdrop-blur-md hover:border-ava-purple/15'
                  ">

                <!-- User message subtle corner accent -->
                <div v-if="msg.sender === 'user'" class="absolute top-0 right-0 w-12 h-12 rounded-tr-[2.2rem] overflow-hidden pointer-events-none">
                  <div class="absolute top-0 right-0 w-full h-[1px] bg-gradient-to-l from-white/10 to-transparent"></div>
                  <div class="absolute top-0 right-0 h-full w-[1px] bg-gradient-to-b from-white/10 to-transparent"></div>
                </div>

                <!-- AVA message glow effect -->
                <div v-if="msg.sender === 'avva'" class="absolute inset-0 rounded-[2.2rem] bg-gradient-to-br from-ava-purple/[0.03] via-transparent to-transparent opacity-0 group-hover/message:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

                <div class="relative z-10">
                  <div v-if="hasCode(msg.text)">
                    <p class="text-[15.5px] leading-[1.7] mb-7 font-medium tracking-tight text-white/90">
                      {{ getTextBeforeCode(msg.text) }}
                    </p>
                    <div class="bg-black/80 rounded-3xl border border-white/[0.06] overflow-hidden shadow-[0_10px_40px_rgba(0,0,0,0.6)] my-5 backdrop-blur-sm">
                      <div
                        class="px-7 py-4 bg-white/[0.02] border-b border-white/[0.05] flex justify-between items-center">
                        <div class="flex items-center gap-3">
                          <div class="flex items-center gap-1.5">
                            <div class="w-2.5 h-2.5 rounded-full bg-red-500/30"></div>
                            <div class="w-2.5 h-2.5 rounded-full bg-amber-500/30"></div>
                            <div class="w-2.5 h-2.5 rounded-full bg-emerald-500/30"></div>
                          </div>
                          <span
                            class="text-[10px] font-black text-white/35 tracking-[0.2em] uppercase ml-2">neural_output.log</span>
                        </div>
                        <button class="text-white/25 hover:text-ava-purple transition-colors p-1.5 hover:bg-white/5 rounded-lg">
                          <Copy :size="14" stroke-width="2.5" />
                        </button>
                      </div>
                      <pre
                        class="p-8 font-mono text-[13px] leading-relaxed overflow-x-auto text-ava-purple/85 selection:bg-ava-purple/30"><code>{{ getCode(msg.text) }}</code></pre>
                    </div>
                    <p v-if="getTextAfterCode(msg.text)"
                      class="text-[15.5px] leading-[1.7] mt-7 font-medium tracking-tight text-white/90">
                      {{ getTextAfterCode(msg.text) }}
                    </p>
                  </div>
                  <p v-else class="text-[15.5px] leading-[1.7] font-medium tracking-tight text-white/90 selection:bg-ava-purple/20">
                    {{ msg.text }}
                  </p>

                  <!-- System Telemetry Overlay -->
                  <div v-if="msg.text.includes('temperature') || msg.text.includes('thermal')"
                    class="mt-7 pt-7 border-t border-white/[0.06] flex flex-wrap gap-7 animate-in fade-in duration-1000">
                    <div class="flex items-center gap-3">
                      <div class="relative">
                        <div class="w-1.5 h-1.5 bg-ava-purple rounded-full shadow-[0_0_8px_#7c3aed]"></div>
                        <div class="absolute inset-0 w-1.5 h-1.5 bg-ava-purple rounded-full animate-ping"></div>
                      </div>
                      <span class="text-[9px] font-black text-white/35 uppercase tracking-[0.22em]">Core_Temp: 54°C</span>
                    </div>
                    <div class="flex items-center gap-3">
                      <div class="w-1.5 h-1.5 rounded-full bg-red-500/60"></div>
                      <span class="text-[9px] font-black text-white/35 uppercase tracking-[0.22em]">Threshold: 85°C</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- User Avatar -->
            <div v-if="msg.sender === 'user'"
              class="w-14 h-14 rounded-2xl bg-gradient-to-br from-white/[0.06] to-white/[0.02] border border-white/10 flex items-center justify-center shadow-xl shrink-0 mt-1 overflow-hidden group-hover/message:border-white/15 transition-all duration-500">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Ghost"
                class="w-full h-full object-cover transition-transform duration-500 group-hover/message:scale-110" alt="You" />
            </div>
          </div>
        </div>
      </div>

      <!-- Thinking Indicator -->
      <div v-if="isThinking" class="flex flex-col items-start animate-in fade-in duration-300 mt-14 ml-2">
        <div class="max-w-[90%] lg:max-w-[82%] flex items-start gap-7">
          <div
            class="w-14 h-14 rounded-2xl bg-gradient-to-br from-black via-black to-ava-purple/10 border border-ava-purple/30 flex items-center justify-center shadow-[0_0_30px_rgba(124,58,237,0.2)] shrink-0 mt-1 relative overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-br from-ava-purple/10 to-transparent animate-pulse"></div>
            <Bot :size="26" class="text-ava-purple relative z-10 animate-pulse" stroke-width="2" />
          </div>

          <div class="flex flex-col items-start">
            <div class="flex items-center gap-3 mb-3.5 px-2">
              <div class="flex items-center gap-2">
                <div class="w-1 h-1 rounded-full bg-ava-purple/40 animate-pulse"></div>
                <span class="text-[9px] font-black tracking-[0.26em] uppercase text-ava-purple/55 animate-pulse">
                  Processing_Query
                </span>
              </div>
            </div>

            <div
              class="relative p-5 rounded-[2.2rem] rounded-tl-lg bg-gradient-to-br from-black/60 via-black/50 to-ava-purple/[0.02] border border-ava-purple/15 backdrop-blur-md flex items-center gap-4 shadow-[0_10px_40px_rgba(124,58,237,0.15)]">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 bg-ava-purple rounded-full animate-bounce [animation-delay:-0.3s] shadow-[0_0_8px_#7c3aed]"></div>
                <div class="w-2 h-2 bg-ava-purple rounded-full animate-bounce [animation-delay:-0.15s] shadow-[0_0_8px_#7c3aed]"></div>
                <div class="w-2 h-2 bg-ava-purple rounded-full animate-bounce shadow-[0_0_8px_#7c3aed]"></div>
              </div>

              <button
                @click="interrupt"
                class="group/btn ml-3 px-5 py-2 bg-red-500/15 border border-red-500/30 rounded-full text-[9px] font-black text-red-400 hover:bg-red-500/25 hover:border-red-500/50 transition-all tracking-[0.18em] shadow-[0_0_15px_rgba(239,68,68,0.1)]">
                <span class="flex items-center gap-2">
                  <span class="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse"></span>
                  Terminate
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Speaking Indicator -->
      <div v-if="isSpeaking" class="flex flex-col items-start animate-in fade-in duration-300 mt-14 ml-2">
        <div class="max-w-[90%] lg:max-w-[82%] flex items-start gap-7">
          <div
            class="w-14 h-14 rounded-2xl bg-gradient-to-br from-black via-black to-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shadow-[0_0_30px_rgba(16,185,129,0.2)] shrink-0 mt-1">
            <Bot :size="26" class="text-emerald-400" stroke-width="2" />
          </div>

          <div class="flex flex-col items-start">
            <div class="flex items-center gap-3 mb-3.5 px-2">
              <div class="flex items-center gap-2">
                <div class="w-1 h-1 rounded-full bg-emerald-400/60 animate-pulse"></div>
                <span class="text-[9px] font-black tracking-[0.26em] uppercase text-emerald-400/70">
                  Voice_Output
                </span>
              </div>
            </div>

            <div class="relative p-5 rounded-[2.2rem] rounded-tl-lg bg-gradient-to-br from-black/60 to-emerald-500/[0.02] border border-emerald-500/15 backdrop-blur-md flex items-center gap-4">
              <div class="flex items-center gap-2">
                <div class="w-1 h-3 bg-emerald-400/60 rounded-full animate-pulse"></div>
                <div class="w-1 h-4 bg-emerald-400/70 rounded-full animate-pulse [animation-delay:-0.2s]"></div>
                <div class="w-1 h-5 bg-emerald-400/80 rounded-full animate-pulse [animation-delay:-0.1s]"></div>
                <div class="w-1 h-4 bg-emerald-400/70 rounded-full animate-pulse [animation-delay:-0.3s]"></div>
                <div class="w-1 h-3 bg-emerald-400/60 rounded-full animate-pulse [animation-delay:-0.15s]"></div>
              </div>

              <button
                @click="interrupt"
                class="ml-3 px-5 py-2 bg-red-500/15 border border-red-500/30 rounded-full text-[9px] font-black text-red-400 hover:bg-red-500/25 transition-all tracking-[0.18em]">
                <span class="flex items-center gap-2">
                  <span class="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse"></span>
                  Terminate
                </span>
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

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'now'
  if (minutes < 60) return `${minutes}m`
  if (hours < 24) return `${hours}h`
  if (days === 1) return '1d'
  if (days < 7) return `${days}d`
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

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
/* Subtle scan line animation */
@keyframes scan {
  0%, 100% { opacity: 0; }
  50% { opacity: 0.1; }
}
</style>
