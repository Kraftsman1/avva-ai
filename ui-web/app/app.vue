<template>
  <div class="h-screen w-screen flex bg-ava-bg text-ava-text overflow-hidden">
    <!-- Sidebar -->
    <AppSidebar class="w-[280px] h-full flex-shrink-0" />
    
    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 relative">
      <!-- Header -->
      <AppHeader />
      
      <!-- Content (Pages) -->
      <main class="flex-1 overflow-hidden relative">
        <NuxtPage />
      </main>
    </div>
  </div>
</template>

<script setup>
// Main layout shell
</script>

<style>
/* Global transitions or base overrides */
.page-enter-active,
.page-leave-active {
  transition: all 0.2s;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>
