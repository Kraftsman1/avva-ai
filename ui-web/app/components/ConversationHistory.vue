<template>
  <div
    class="fixed left-0 top-0 h-full w-80 bg-black/98 border-r border-white/[0.08] transform transition-all duration-500 ease-out z-[50] backdrop-blur-xl shadow-[0_0_40px_rgba(0,0,0,0.5)]"
    :class="isOpen ? 'translate-x-0' : '-translate-x-full'">

    <!-- Ambient glow effect -->
    <div class="absolute inset-0 bg-gradient-to-b from-ava-purple/[0.02] via-transparent to-transparent pointer-events-none"></div>

    <!-- Left edge accent -->
    <div class="absolute left-0 top-0 bottom-0 w-[1px] bg-gradient-to-b from-ava-purple/50 via-ava-purple/20 to-transparent"></div>

    <div class="flex flex-col h-full relative">
      <!-- Header -->
      <div class="p-6 border-b border-white/[0.08] relative">
        <!-- Decorative corner accents -->
        <div class="absolute top-0 left-0 w-16 h-[1px] bg-gradient-to-r from-ava-purple/50 to-transparent"></div>
        <div class="absolute top-0 left-0 w-[1px] h-16 bg-gradient-to-b from-ava-purple/50 to-transparent"></div>

        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-3">
            <div class="w-1 h-1 bg-ava-purple rounded-full shadow-[0_0_8px_#7c3aed]"></div>
            <h2 class="text-[11px] font-black tracking-[0.28em] uppercase text-ava-purple/90">
              Memory Archive
            </h2>
          </div>
          <Button
            variant="ghost"
            size="icon"
            @click="$emit('close')"
            class="h-8 w-8 hover:bg-white/[0.05] hover:text-white/80 text-white/40 rounded-lg transition-all duration-200">
            <X :size="16" stroke-width="2.5" />
          </Button>
        </div>

        <Button
          @click="startNew"
          class="group w-full bg-gradient-to-r from-ava-purple/15 to-ava-purple/10 border border-ava-purple/30 hover:border-ava-purple/50 hover:from-ava-purple/20 hover:to-ava-purple/15 text-ava-purple text-[10px] font-black tracking-[0.18em] uppercase py-2.5 rounded-xl transition-all duration-300 shadow-[0_0_20px_rgba(124,58,237,0.1)] hover:shadow-[0_0_30px_rgba(124,58,237,0.2)] relative overflow-hidden">
          <span class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.03] to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></span>
          <span class="relative flex items-center justify-center gap-2">
            <span class="text-[14px] leading-none">+</span>
            <span>Initialize Session</span>
          </span>
        </Button>
      </div>

      <!-- Search -->
      <div class="px-4 py-4 border-b border-white/[0.05]">
        <div class="relative group">
          <Search :size="13" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30 group-focus-within:text-ava-purple/60 transition-colors duration-200" />
          <input
            v-model="searchQuery"
            @input="handleSearch"
            type="text"
            placeholder="SEARCH NEURAL_INDEX..."
            class="w-full bg-white/[0.03] border border-white/[0.08] focus:border-ava-purple/40 rounded-xl py-2.5 pl-10 pr-4 text-[11px] text-white/80 placeholder:text-white/20 placeholder:tracking-[0.15em] outline-none transition-all duration-200 focus:bg-white/[0.05] font-medium"
          />
        </div>
      </div>

      <!-- Conversation List -->
      <ScrollArea class="flex-1">
        <div class="p-4 space-y-2">
          <!-- Pinned Section Header -->
          <div
            v-if="conversations.some(s => s.pinned)"
            class="flex items-center gap-2 px-2 py-2 mb-1">
            <div class="w-3 h-[1px] bg-gradient-to-r from-transparent to-ava-purple/30"></div>
            <span class="text-[8px] font-black text-ava-purple/50 tracking-[0.2em] uppercase">Pinned</span>
            <div class="flex-1 h-[1px] bg-gradient-to-r from-ava-purple/30 to-transparent"></div>
          </div>

          <div
            v-for="(session, index) in conversations"
            :key="session.id"
            @click="selectConversation(session.id)"
            class="group relative p-4 rounded-xl cursor-pointer transition-all duration-300 border"
            :class="[
              currentId === session.id
                ? 'bg-ava-purple/[0.12] border-ava-purple/40 shadow-[0_0_20px_rgba(124,58,237,0.15)]'
                : 'border-transparent hover:bg-white/[0.03] hover:border-white/[0.08]',
              session.pinned && 'bg-white/[0.02]'
            ]"
            :style="{ animationDelay: `${index * 30}ms` }">

            <!-- Hover glow effect -->
            <div
              v-if="currentId === session.id"
              class="absolute inset-0 bg-gradient-to-r from-ava-purple/[0.08] via-transparent to-ava-purple/[0.08] rounded-xl pointer-events-none animate-pulse"></div>

            <div class="relative">
              <!-- Title Row -->
              <div class="flex items-start justify-between mb-2.5">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <Pin
                    v-if="session.pinned"
                    :size="9"
                    class="text-ava-purple shrink-0 animate-in fade-in duration-300"
                    :style="{ fill: 'currentColor' }" />
                  <span class="text-[11px] font-semibold text-white/85 truncate leading-tight tracking-tight">
                    {{ session.title || 'Untitled Session' }}
                  </span>
                </div>
                <span class="text-[8px] font-black text-white/25 tracking-[0.12em] shrink-0 ml-3 uppercase">
                  {{ formatDate(session.updated_at) }}
                </span>
              </div>

              <!-- Meta Row -->
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-1 h-1 rounded-full bg-white/20"></div>
                  <span class="text-[9px] text-white/40 capitalize tracking-wide font-medium">
                    {{ session.brain_id || 'Local_Core' }}
                  </span>
                </div>

                <!-- Action Buttons -->
                <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0">
                  <Button
                    variant="ghost"
                    size="icon"
                    @click.stop="exportConv(session.id)"
                    class="h-7 w-7 hover:bg-green-500/10 hover:text-green-400 text-white/30 rounded-lg transition-all duration-200"
                    title="Export Data">
                    <Download :size="11" stroke-width="2.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    @click.stop="togglePin(session.id)"
                    class="h-7 w-7 hover:bg-ava-purple/10 hover:text-ava-purple text-white/30 rounded-lg transition-all duration-200"
                    :title="session.pinned ? 'Unpin' : 'Pin to Archive'">
                    <component :is="session.pinned ? PinOff : Pin" :size="11" stroke-width="2.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    @click.stop="deleteConv(session.id)"
                    class="h-7 w-7 hover:bg-red-500/10 hover:text-red-400 text-white/30 rounded-lg transition-all duration-200"
                    title="Delete Session">
                    <Trash2 :size="11" stroke-width="2.5" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="conversations.length === 0" class="flex flex-col items-center justify-center py-16 px-6">
            <div class="w-16 h-16 rounded-2xl bg-white/[0.02] border border-white/[0.05] flex items-center justify-center mb-4">
              <Search :size="24" class="text-white/10" />
            </div>
            <p class="text-[11px] text-white/30 text-center tracking-wide font-medium">
              Neural archive empty
            </p>
            <p class="text-[9px] text-white/20 text-center mt-1 tracking-wider">
              Start a conversation to begin
            </p>
          </div>
        </div>
      </ScrollArea>

      <!-- Footer Stats -->
      <div class="p-4 border-t border-white/[0.05] bg-black/50 relative">
        <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-ava-purple/20 to-transparent"></div>

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-1 h-1 bg-white/20 rounded-full"></div>
            <span class="text-[8px] font-black text-white/25 tracking-[0.15em] uppercase">
              Memory_Index
            </span>
          </div>
          <span class="text-[9px] font-bold text-ava-purple/60 tracking-wider">
            {{ conversations.length }} {{ conversations.length === 1 ? 'session' : 'sessions' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Search, X, Trash2, Pin, PinOff, Download } from 'lucide-vue-next'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'select'])

const { $ava } = useNuxtApp()

const searchQuery = ref('')
const currentId = computed(() => $ava?.state?.currentConversationId)
const conversations = computed(() => $ava?.state?.conversations || [])

onMounted(() => {
  $ava?.fetchConversations?.()
})

watch(() => props.isOpen, (val) => {
  if (val) {
    $ava?.fetchConversations?.()
  }
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date

  if (diff < 86400000) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (diff < 604800000) {
    return date.toLocaleDateString([], { weekday: 'short' })
  }
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

const selectConversation = (id) => {
  $ava?.loadConversation?.(id)
  emit('select', id)
  emit('close')
}

const deleteConv = (id) => {
  if (confirm('Delete this conversation?')) {
    $ava?.deleteConversation?.(id)
  }
}

const startNew = () => {
  $ava?.startConversation?.('New Conversation')
  emit('select', null)
  emit('close')
}

const togglePin = (id) => {
  $ava?.togglePin?.(id)
}

const exportConv = (id) => {
  const session = conversations.value.find(s => s.id === id)
  const title = session?.title || 'conversation'

  // Show export format selection
  const format = confirm('Export as Markdown?\n\nOK = Markdown\nCancel = JSON') ? 'markdown' : 'json'
  $ava?.exportConversation?.(id, format, title)
}

let searchTimeout = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.trim()) {
      $ava?.searchConversations?.(searchQuery.value)
    } else {
      $ava?.fetchConversations?.()
    }
  }, 300)
}
</script>

<style scoped>
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>
