<template>
  <div
    class="relative border rounded-2xl p-6 bg-gradient-to-br from-black/40 to-black/20 backdrop-blur-md transition-all duration-300"
    :class="[
      workflow.status === 'awaiting_approval' ? 'border-ava-purple/40 shadow-[0_0_30px_rgba(124,58,237,0.2)]' : 'border-white/[0.08]',
      workflow.status === 'executing' ? 'border-emerald-400/40 shadow-[0_0_30px_rgba(52,211,153,0.2)]' : '',
      workflow.status === 'failed' ? 'border-red-400/40 shadow-[0_0_30px_rgba(239,68,68,0.2)]' : ''
    ]">

    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <div
            class="w-2 h-2 rounded-full"
            :class="{
              'bg-ava-purple shadow-[0_0_8px_#7c3aed] animate-pulse': workflow.status === 'awaiting_approval',
              'bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse': workflow.status === 'executing',
              'bg-gray-400': workflow.status === 'completed',
              'bg-red-400 shadow-[0_0_8px_#ef4444]': workflow.status === 'failed'
            }"></div>
          <h3 class="text-base font-bold text-white tracking-tight">{{ workflow.title }}</h3>
        </div>
        <p class="text-xs text-white/50 tracking-wide">{{ workflow.description }}</p>
      </div>

      <div
        class="px-3 py-1.5 rounded-lg text-[9px] font-black tracking-[0.15em] uppercase border"
        :class="{
          'bg-ava-purple/10 border-ava-purple/30 text-ava-purple': workflow.status === 'awaiting_approval',
          'bg-emerald-400/10 border-emerald-400/30 text-emerald-400': workflow.status === 'executing',
          'bg-gray-400/10 border-gray-400/30 text-gray-400': workflow.status === 'completed',
          'bg-red-400/10 border-red-400/30 text-red-400': workflow.status === 'failed'
        }">
        {{ workflow.status.replace('_', ' ') }}
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="workflow.status !== 'awaiting_approval'" class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[10px] font-black text-white/40 tracking-[0.15em] uppercase">Progress</span>
        <span class="text-xs font-bold text-ava-purple font-mono">{{ progress.progress_percent.toFixed(0) }}%</span>
      </div>
      <div class="h-2 w-full bg-white/[0.05] rounded-full overflow-hidden border border-white/[0.08]">
        <div
          class="h-full bg-gradient-to-r from-ava-purple to-[#9333ea] transition-all duration-500 shadow-[0_0_10px_rgba(124,58,237,0.4)]"
          :style="{ width: progress.progress_percent + '%' }"></div>
      </div>
      <div class="flex items-center justify-between mt-1.5">
        <span class="text-[9px] text-white/30">{{ progress.completed_steps }}/{{ progress.total_steps }} steps</span>
        <span v-if="progress.failed_steps > 0" class="text-[9px] text-red-400">{{ progress.failed_steps }} failed</span>
      </div>
    </div>

    <!-- Steps List -->
    <div class="space-y-2 mb-6 max-h-64 overflow-y-auto">
      <div
        v-for="(step, index) in workflow.steps"
        :key="step.id"
        class="flex items-start gap-3 p-3 rounded-xl transition-all border"
        :class="{
          'bg-white/[0.02] border-white/[0.05]': step.status === 'pending',
          'bg-emerald-400/5 border-emerald-400/20': step.status === 'in_progress',
          'bg-white/[0.02] border-white/[0.05]': step.status === 'completed',
          'bg-red-400/5 border-red-400/20': step.status === 'failed'
        }">

        <!-- Step Number/Status Icon -->
        <div
          class="flex-shrink-0 w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-black border"
          :class="{
            'bg-white/[0.03] border-white/[0.08] text-white/30': step.status === 'pending',
            'bg-emerald-400/10 border-emerald-400/30 text-emerald-400': step.status === 'in_progress',
            'bg-ava-purple/10 border-ava-purple/30 text-ava-purple': step.status === 'completed',
            'bg-red-400/10 border-red-400/30 text-red-400': step.status === 'failed'
          }">
          <span v-if="step.status === 'pending'">{{ index + 1 }}</span>
          <CheckCircle v-else-if="step.status === 'completed'" :size="14" />
          <Loader v-else-if="step.status === 'in_progress'" :size="14" class="animate-spin" />
          <AlertCircle v-else-if="step.status === 'failed'" :size="14" />
        </div>

        <!-- Step Info -->
        <div class="flex-1 min-w-0">
          <div class="text-xs font-semibold text-white/80 mb-1 tracking-tight">{{ step.description }}</div>
          <div class="text-[10px] text-white/40 tracking-wide">{{ step.action }}</div>

          <!-- Step Result -->
          <div v-if="step.result" class="mt-2 p-2 bg-black/30 rounded-lg border border-white/[0.05]">
            <div class="text-[10px] text-white/60 tracking-wide line-clamp-2">{{ step.result }}</div>
          </div>

          <!-- Step Error -->
          <div v-if="step.error" class="mt-2 p-2 bg-red-500/10 rounded-lg border border-red-400/20">
            <div class="text-[10px] text-red-400 tracking-wide">{{ step.error }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="workflow.status === 'awaiting_approval'" class="flex items-center gap-3">
      <Button
        @click="$emit('approve', workflow.id)"
        class="flex-1 bg-gradient-to-r from-ava-purple/20 to-ava-purple/15 border border-ava-purple/40 hover:border-ava-purple/60 hover:from-ava-purple/30 hover:to-ava-purple/20 text-ava-purple text-[10px] font-black tracking-[0.15em] uppercase py-3 rounded-xl transition-all duration-300 shadow-[0_0_20px_rgba(124,58,237,0.15)] hover:shadow-[0_0_30px_rgba(124,58,237,0.3)] relative overflow-hidden group">
        <span class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.05] to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></span>
        <span class="relative flex items-center justify-center gap-2">
          <Play :size="14" />
          <span>Execute Workflow</span>
        </span>
      </Button>

      <Button
        @click="$emit('cancel', workflow.id)"
        variant="ghost"
        class="px-4 py-3 hover:bg-red-500/10 hover:text-red-400 text-white/40 rounded-xl transition-all border border-transparent hover:border-red-400/20">
        <X :size="16" />
      </Button>
    </div>

    <div v-else-if="workflow.status === 'executing'" class="flex items-center gap-3">
      <Button
        @click="$emit('cancel', workflow.id)"
        variant="ghost"
        class="w-full hover:bg-red-500/10 hover:text-red-400 hover:border-red-400/20 text-white/60 text-[10px] font-black tracking-[0.15em] uppercase py-3 rounded-xl transition-all border border-white/[0.08]">
        <span class="flex items-center justify-center gap-2">
          <StopCircle :size="14" />
          <span>Cancel Workflow</span>
        </span>
      </Button>
    </div>
  </div>
</template>

<script setup>
import { CheckCircle, AlertCircle, Loader, Play, X, StopCircle } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
  workflow: {
    type: Object,
    required: true
  }
})

defineEmits(['approve', 'cancel'])

const progress = computed(() => {
  const total = props.workflow.steps.length
  const completed = props.workflow.steps.filter(s => s.status === 'completed').length
  const failed = props.workflow.steps.filter(s => s.status === 'failed').length
  const in_progress = props.workflow.steps.filter(s => s.status === 'in_progress').length

  return {
    total_steps: total,
    completed_steps: completed,
    failed_steps: failed,
    in_progress_steps: in_progress,
    progress_percent: total > 0 ? (completed / total * 100) : 0
  }
})
</script>
