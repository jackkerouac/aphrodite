<template>
  <div class="flex justify-between items-center p-4 bg-base-200 rounded-lg">
    <div>
      <div class="font-semibold">Uptime</div>
      <div>{{ uptime }}</div>
    </div>
    <div class="text-right">
      <svg xmlns="http://www.w3.org/2000/svg" 
           class="h-8 w-8 text-success" 
           fill="none" 
           viewBox="0 0 24 24" 
           stroke="currentColor">
        <path stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UptimeInfo',
  props: {
    uptime: {
      type: String,
      default: 'Unknown'
    }
  }
}
</script>
