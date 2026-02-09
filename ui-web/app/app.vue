<template>
  <div class="h-screen w-screen flex bg-ava-bg text-ava-text overflow-hidden relative">
    <ConversationHistory :is-open="showHistory" @close="showHistory = false" />

    <!-- Overlay backdrop when conversation history is open -->
    <Transition
      enter-active-class="transition-opacity duration-300"
      leave-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showHistory"
        @click="showHistory = false"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[35] opacity-100">
      </div>
    </Transition>

    <ErrorToast />
    <SuccessToast />
    <!-- Sidebar -->
    <AppSidebar class="w-[280px] h-full flex-shrink-0" />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 relative">
      <!-- Header -->
      <AppHeader @toggle-history="showHistory = !showHistory" />

      <!-- Content (Pages) -->
      <main class="flex-1 overflow-hidden relative">
        <NuxtPage />
      </main>
    </div>
  </div>
</template>

<script setup>
const showHistory = ref(false)
</script>

<style>
/* Global transitions or base overrides */
.page-enter-active,
.page-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-5px) scale(1.02);
}
</style>
