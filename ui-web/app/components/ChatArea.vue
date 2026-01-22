<template>
  <ScrollArea class="flex-1 h-full" ref="scrollContainer">
    <div class="flex-1 flex flex-col p-10 pb-36 max-w-5xl mx-auto w-full font-sans">
      <!-- Session Start Indicator -->
      <div class="flex justify-center mb-16">
        <div class="px-6 py-2 bg-[#12121e]/50 border border-white/5 rounded-full flex items-center gap-3">
          <span class="text-[9px] font-black text-white/40 tracking-[0.2em] uppercase">
            SESSION: {{ currentSessionLabel }}
          </span>
        </div>
      </div>

      <!-- Messages -->
      <div class="space-y-10">
        <div v-for="msg in $ava?.state?.messages || []" :key="msg.id"
          class="flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500"
          :class="msg.sender === 'user' ? 'items-end' : 'items-start'">
          <!-- Message Group -->
          <div class="max-w-[85%] flex items-start gap-5" :class="msg.sender === 'user' ? 'flex-row-reverse' : ''">
            <!-- Icon/Avatar for AVA -->
            <div v-if="msg.sender !== 'user'"
              class="w-10 h-10 rounded-xl bg-[#2a1a4a] border border-[#7c3aed33] flex items-center justify-center shadow-lg shrink-0 mt-1">
              <Bot :size="20" class="text-[#7c3aed]" />
            </div>

            <div class="flex flex-col" :class="msg.sender === 'user' ? 'items-end' : 'items-start'">
              <!-- Attribution -->
              <span class="text-[10px] font-black tracking-widest uppercase mb-2 px-1"
                :class="msg.sender === 'user' ? 'text-white/40' : 'text-[#7c3aed]'">
                {{ msg.sender === 'user' ? 'YOU' : 'AVA' }}
              </span>

              <!-- Content Bubble -->
              <div class="p-6 rounded-2xl transition-all" :class="msg.sender === 'user'
                  ? 'bubble-user rounded-tr-none'
                  : 'bubble-ava rounded-tl-none border-[#7c3aed11]'
                ">
                <div v-if="hasCode(msg.text)">
                  <p class="text-[15px] leading-relaxed mb-4 font-medium">{{ getTextBeforeCode(msg.text) }}</p>
                  <div class="bg-[#07070a] rounded-xl border border-white/5 overflow-hidden shadow-2xl">
                    <div class="px-4 py-2 bg-white/[0.03] border-b border-white/5 flex justify-between items-center">
                      <span class="text-[10px] font-mono text-white/40 tracking-wider">shell_script.sh</span>
                      <Copy :size="14" class="text-white/20 hover:text-white cursor-pointer transition-colors" />
                    </div>
                    <pre
                      class="p-6 font-mono text-sm overflow-x-auto text-[#a78bfa]"><code>{{ getCode(msg.text) }}</code></pre>
                  </div>
                  <p v-if="getTextAfterCode(msg.text)" class="text-[15px] leading-relaxed mt-4 font-medium">
                    {{ getTextAfterCode(msg.text) }}
                  </p>
                </div>
                <p v-else class="text-[15px] leading-relaxed font-medium tracking-tight">
                  {{ msg.text }}
                </p>

                <!-- Status Indicators for AVA stats if any (Mocked for visual fidelity as per screenshot) -->
                <div v-if="msg.text.includes('temperature')" class="mt-4 pt-4 border-t border-white/5 flex gap-4">
                  <div class="flex items-center gap-2">
                    <div class="w-1.5 h-1.5 rounded-full bg-[#7c3aed]"></div>
                    <span class="text-[10px] font-bold text-white/40 uppercase tracking-widest">TEMP: 54°C</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <div class="w-1.5 h-1.5 rounded-full bg-[#ef4444]"></div>
                    <span class="text-[10px] font-bold text-white/40 uppercase tracking-widest">THRESHOLD: 85°C</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- User Avatar (Mockup style) -->
            <div v-if="msg.sender === 'user'"
              class="w-10 h-10 rounded-xl bg-[#1a1a2e] border border-white/10 flex items-center justify-center shadow-lg shrink-0 mt-1 overflow-hidden">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Ghost" class="w-full h-full object-cover"
                alt="You" />
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

const currentSessionLabel = 'LINUX ENVIRONMENT OPTIMIZATION'

const hasCode = (text) => text.includes('```')
const getCode = (text) => text.split('```')[1]?.split('\n').splice(1).join('\n')
const getTextBeforeCode = (text) => text.split('```')[0]
const getTextAfterCode = (text) => text.split('```')[2]

watch(
  () => $ava?.state?.messages?.length,
  () => {
    nextTick(() => {
      const viewport = scrollContainer.value?.$el?.querySelector('[data-radix-scroll-area-viewport]')
      if (viewport) {
        viewport.scrollTop = viewport.scrollHeight
      }
    })
  }
)
</script>
