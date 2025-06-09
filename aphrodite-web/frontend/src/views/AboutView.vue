<template>
  <div class="about-page">
    <h1 class="text-3xl font-bold mb-6">About Aphrodite</h1>
    
    <!-- System Details Section -->
    <SystemDetailsCard />
    
    <!-- Links Section -->
    <LinksCard />
    
    <!-- Acknowledgments Section -->
    <div class="mt-6">
      <AcknowledgmentsCard />
    </div>
  </div>
</template>

<script>
import SystemDetailsCard from '@/components/about/SystemDetailsCard.vue'
import LinksCard from '@/components/about/LinksCard.vue'
import AcknowledgmentsCard from '@/components/about/AcknowledgmentsCard.vue'

export default {
  name: 'AboutView',
  components: {
    SystemDetailsCard,
    LinksCard,
    AcknowledgmentsCard
  }
}
</script>

<style scoped>
.about-page {
  max-width: 800px;
  margin: 0 auto;
}
</style>
