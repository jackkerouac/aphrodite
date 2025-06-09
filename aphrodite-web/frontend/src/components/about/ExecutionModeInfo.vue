<template>
  <div class="flex justify-between items-center p-4 bg-base-200 rounded-lg">
    <div>
      <div class="font-semibold">Execution Mode</div>
      <div class="flex items-center gap-2">
        <span class="badge" :class="getBadgeClass(executionMode)">
          {{ executionMode }}
        </span>
      </div>
    </div>
    <div class="text-right">
      <svg v-if="executionMode === 'Docker'" 
           xmlns="http://www.w3.org/2000/svg" 
           class="h-8 w-8 text-blue-500" 
           viewBox="0 0 24 24" 
           fill="currentColor">
        <path d="M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185m-2.954-5.43h2.118a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.186m0 2.716h2.118a.187.187 0 00.186-.186V6.29a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.887c0 .102.082.185.185.186m-2.93 0h2.12a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H8.1a.185.185 0 00-.185.185v1.887c0 .102.083.185.185.186m-2.964 0h2.119a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H5.136a.186.186 0 00-.186.185v1.887c0 .102.084.185.186.186m5.893 2.715h2.118a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m-2.93 0h2.12a.185.185 0 00.185-.185V9.006a.185.185 0 00-.185-.186H8.1a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185m-2.964 0h2.119a.185.185 0 00.185-.185V9.006a.185.185 0 00-.185-.186H5.136a.186.186 0 00-.186.186v1.887c0 .102.084.185.186.185M2.17 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186H2.17a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185"/>
      </svg>
      <svg v-else 
           xmlns="http://www.w3.org/2000/svg" 
           class="h-8 w-8 text-green-500" 
           fill="none" 
           viewBox="0 0 24 24" 
           stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExecutionModeInfo',
  props: {
    executionMode: {
      type: String,
      default: 'Unknown'
    }
  },
  methods: {
    getBadgeClass(mode) {
      switch (mode) {
        case 'Docker':
          return 'badge-primary'
        case 'Development':
          return 'badge-warning'
        case 'Installed Package':
          return 'badge-success'
        default:
          return 'badge-ghost'
      }
    }
  }
}
</script>
