<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-2xl mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
        Acknowledgments
      </h2>
      
      <div class="space-y-3">
        <div class="p-4 bg-base-200 rounded-lg">
          <div class="flex items-start gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mt-1 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div class="flex-1">
              <div class="font-semibold">One-Liners Dataset</div>
              <div class="text-sm opacity-70 mb-2">
                Movie and TV show one-liner quotes used for enhanced functionality
              </div>
              <div class="flex items-center gap-2">
                <span class="text-sm">by</span>
                <a href="https://github.com/antoniaelek" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   class="link link-primary text-sm font-medium">
                  Antonija Elek
                </a>
              </div>
              <a href="https://github.com/antoniaelek/one-liners" 
                 target="_blank" 
                 rel="noopener noreferrer"
                 class="btn btn-xs btn-outline btn-primary mt-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                View Repository
              </a>
            </div>
          </div>
        </div>
        
        <!-- Future acknowledgments can be added here -->
        <div class="text-center text-sm opacity-60 mt-4">
          <p>We appreciate the open-source community and the creators who make their work freely available.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AcknowledgmentsCard'
}
</script>
