<template>
  <div class="home">
    <h1 class="text-2xl font-bold mb-4">Aphrodite Dashboard</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-lg font-semibold mb-2">System Status</h2>
        <p>Jellyfin: Not Connected</p>
      </div>
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-lg font-semibold mb-2">Quick Stats</h2>
        <p>Jobs: 0</p>
      </div>
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-lg font-semibold mb-2">Quick Actions</h2>
        <button class="bg-blue-500 text-white px-3 py-1 rounded">Check Connection</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  components: {
  }
}
</script>
