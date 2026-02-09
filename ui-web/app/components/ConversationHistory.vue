<template>
  <div
    class="fixed left-0 top-0 h-full w-80 bg-black/90 border-r border-white/[0.05] transform transition-transform duration-300 z-50"
    :class="isOpen ? 'translate-x-0' : '-translate-x-full'">
    <div class="flex flex-col h-full">
      <!-- Header -->
      <div class="p-6 border-b border-white/[0.05]">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-[12px] font-black tracking-[0.25em] uppercase text-ava-purple">
            Conversation History
          </h2>
          <Button variant="ghost" size="icon" @click="$emit('close')" class="h-8 w-8">
            <X :size="16" class="text-white/40" />
          </Button>
        </div>
        <Button @click="startNew" class="w-full bg-ava-purple/20 border border-ava-purple/40 hover:bg-ava-purple/30 text-ava-purple text-[10px] font-black tracking-[0.15em] uppercase">
          + New Conversation
        </Button>
      </div>

      <!-- Search -->
      <div class="p-4 border-b border-white/[0.05]">
        <div class="relative">
          <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
          <input
            v-model="searchQuery"
            @input="handleSearch"
            type="text"
            placeholder="Search conversations..."
            class="w-full bg-white/[0.02] border border-white/[0.05] rounded-xl py-2 pl-9 pr-4 text-[12px] text-white/70 placeholder:text-white/20 outline-none focus:border-ava-purple/30 transition-colors"
          />
        </div>
      </div>

      <!-- Conversation List -->
      <ScrollArea class="flex-1">
        <div class="p-4 space-y-2">
          <div
            v-for="session in conversations"
            :key="session.id"
            @click="selectConversation(session.id)"
            class="group p-4 rounded-xl cursor-pointer transition-all border border-transparent"
            :class="currentId === session.id ? 'bg-ava-purple/10 border-ava-purple/30' : 'hover:bg-white/[0.02] hover:border-white/[0.05]'">
            <div class="flex items-start justify-between mb-2">
              <div class="flex items-center gap-1.5 flex-1 min-w-0">
                <Pin v-if="session.pinned" :size="10" class="text-ava-purple shrink-0" />
                <span class="text-[11px] font-medium text-white/80 truncate">
                  {{ session.title || 'Untitled' }}
                </span>
              </div>
              <span class="text-[9px] font-black text-white/20 tracking-[0.1em] shrink-0 ml-2">
                {{ formatDate(session.updated_at) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[9px] text-white/30 capitalize">{{ session.brain_id || 'Local' }}</span>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  variant="ghost"
                  size="icon"
                  @click.stop="exportConv(session.id)"
                  class="h-6 w-6"
                  title="Export">
                  <Download :size="12" class="text-white/30 hover:text-green-400" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  @click.stop="togglePin(session.id)"
                  class="h-6 w-6"
                  :title="session.pinned ? 'Unpin' : 'Pin'">
                  <component :is="session.pinned ? PinOff : Pin" :size="12" class="text-white/30 hover:text-ava-purple" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  @click.stop="deleteConv(session.id)"
                  class="h-6 w-6">
                  <Trash2 :size="12" class="text-white/30 hover:text-red-400" />
                </Button>
              </div>
            </div>
          </div>

          <div v-if="conversations.length === 0" class="text-center py-8">
            <p class="text-[11px] text-white/30">No conversations yet</p>
          </div>
        </div>
      </ScrollArea>

      <!-- Footer -->
      <div class="p-4 border-t border-white/[0.05]">
        <p class="text-[9px] text-white/20 text-center tracking-[0.1em]">
          {{ conversations.length }} conversations
        </p>
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
