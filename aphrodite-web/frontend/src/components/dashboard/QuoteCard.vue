<template>
  <div class="quote-card bg-base-200 p-4 rounded-lg border border-base-300 mb-6">
    <div v-if="loading" class="flex items-center justify-center">
      <span class="loading loading-spinner loading-sm mr-2"></span>
      <span>Loading quote...</span>
    </div>
    
    <div v-else-if="error" class="text-warning">
      <div class="flex items-center">
        <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        Could not load quote
      </div>
    </div>
    
    <div v-else class="quote-content">
      <div class="flex items-start">
        <div class="text-4xl text-primary mr-3 leading-none">"</div>
        <div class="flex-1">
          <p class="text-base italic text-base-content/80 leading-relaxed">{{ quote }}</p>
          <div class="mt-2 text-xs text-base-content/60" v-if="totalQuotes">
            Quote {{ currentQuoteIndex }} of {{ totalQuotes }}
          </div>
        </div>
        <div class="text-4xl text-primary ml-3 leading-none">"</div>
      </div>
      
      <div class="mt-3 flex justify-end">
        <button 
          @click="loadNewQuote" 
          class="btn btn-ghost btn-xs"
          :disabled="loading"
        >
          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          New Quote
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import api from '@/api';

export default {
  name: 'QuoteCard',
  setup() {
    const quote = ref('');
    const loading = ref(true);
    const error = ref(false);
    const totalQuotes = ref(null);
    const currentQuoteIndex = ref(null);

    const loadQuote = async () => {
      try {
        loading.value = true;
        error.value = false;
        
        const response = await api.quotes.getRandomQuote();
        
        if (response.error) {
          console.warn('Quote API returned error:', response.error);
        }
        
        quote.value = response.quote;
        totalQuotes.value = response.total_quotes;
        
        // Generate a random quote index for display (not the actual index)
        if (totalQuotes.value) {
          currentQuoteIndex.value = Math.floor(Math.random() * totalQuotes.value) + 1;
        }
        
      } catch (err) {
        console.error('Failed to load quote:', err);
        error.value = true;
        quote.value = 'Welcome to Aphrodite - enhancing your media experience!';
      } finally {
        loading.value = false;
      }
    };

    const loadNewQuote = () => {
      loadQuote();
    };

    onMounted(() => {
      loadQuote();
    });

    return {
      quote,
      loading,
      error,
      totalQuotes,
      currentQuoteIndex,
      loadNewQuote
    };
  }
};
</script>

<style scoped>
.quote-card {
  transition: all 0.2s ease;
}

.quote-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.quote-content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
