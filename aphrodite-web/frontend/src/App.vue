<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Navigation -->
    <nav class="bg-blue-600 text-white shadow-md">
      <div class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="text-xl font-bold">Aphrodite</div>
        <div class="space-x-4">
          <a href="#" class="hover:text-blue-200">Dashboard</a>
          <a href="#" class="hover:text-blue-200">Settings</a>
          <a href="#" class="hover:text-blue-200">Execute</a>
          <a href="#" class="hover:text-blue-200">Preview</a>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 py-6">
      <h1 class="text-2xl font-bold mb-4">Aphrodite Web Wrapper</h1>
      <p class="mb-4">Welcome to the Aphrodite Web Wrapper. This application provides a user-friendly interface for managing the Aphrodite-Python script.</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white p-4 rounded shadow">
          <h2 class="text-lg font-semibold mb-2">Getting Started</h2>
          <p>This is a placeholder dashboard for the Aphrodite Web Wrapper.</p>
        </div>
        
        <div class="bg-white p-4 rounded shadow">
          <h2 class="text-lg font-semibold mb-2">Quick Actions</h2>
          <button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">Check Connection</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Any global styles can go here */
</style>
