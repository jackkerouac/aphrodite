<template>
  <div class="flex justify-between items-center p-4 bg-base-200 rounded-lg">
    <div>
      <div class="font-semibold">Database Schema</div>
      <div class="font-mono text-sm">{{ schemaHash }}</div>
    </div>
    <div class="text-right">
      <svg xmlns="http://www.w3.org/2000/svg" 
           class="h-8 w-8 text-primary" 
           fill="none" 
           viewBox="0 0 24 24" 
           stroke="currentColor">
        <path stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DatabaseSchemaInfo',
  props: {
    schemaHash: {
      type: String,
      default: 'Unknown'
    }
  }
}
</script>
