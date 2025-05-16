<template>
  <div class="min-h-screen bg-base-200 flex" data-theme="cupcake">
    <!-- Left Side Navigation -->
    <div class="drawer lg:drawer-open">
      <input id="my-drawer" type="checkbox" class="drawer-toggle" />
      <div class="drawer-content flex flex-col">
        <!-- Top Navigation Bar (Mobile) -->
        <div class="navbar bg-primary text-primary-content lg:hidden">
          <div class="flex-none">
            <label for="my-drawer" class="btn btn-square btn-ghost">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </label>
          </div>
          <div class="flex-1">
            <span class="text-xl font-bold">Aphrodite</span>
          </div>
          <div class="flex-none">
            <div class="dropdown dropdown-end">
              <div tabindex="0" role="button" class="btn btn-ghost btn-circle">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              </div>
              <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                <li><a data-set-theme="light">Light</a></li>
                <li><a data-set-theme="dark">Dark</a></li>
                <li><a data-set-theme="cupcake">Cupcake</a></li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Page Content -->
        <div class="p-4 w-full min-h-screen max-w-screen-xl mx-auto overflow-y-auto">
          <!-- Router View - This is where page components will be rendered -->
          <router-view />

          <!-- Footer -->
          <footer class="footer footer-center p-4 mt-8 text-base-content opacity-70">
            <div>
              <p>Aphrodite Web Wrapper © 2025</p>
            </div>
          </footer>
        </div>
      </div>

      <!-- Sidebar Content -->
      <div class="drawer-side z-10">
        <label for="my-drawer" class="drawer-overlay"></label>
        <div class="bg-base-100 w-80 min-h-screen">
          <div class="navbar bg-primary text-primary-content">
            <div class="flex-1 px-2 mx-2 text-xl font-bold">Aphrodite</div>
          </div>
          <div class="px-4 py-6">
            <div class="flex flex-col items-center mb-6">
              <div class="avatar">
                <div class="w-24 mask mask-squircle bg-gray-300 flex items-center justify-center">
                  <!-- Replaced placeholder image with a text avatar -->
                  <span class="text-2xl font-bold text-gray-600">J</span>
                </div>
              </div>
              <h2 class="mt-2 text-xl font-bold">Jellyfin</h2>
              <p class="text-sm opacity-70">Connected</p>
            </div>
            
            <ul class="menu bg-base-100 menu-lg rounded-box">
              <li class="menu-title">Main Menu</li>
              <li>
                <router-link to="/" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
                  Dashboard
                </router-link>
              </li>
              <li>
                <router-link to="/settings" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
                  Settings
                </router-link>
              </li>
              <li>
                <router-link to="/execute" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                  Execute
                </router-link>
              </li>
              <li>
                <router-link to="/preview" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                  Preview
                </router-link>
              </li>
              
              <li class="menu-title mt-4">Badge Types</li>
              <li>
                <router-link to="/settings" :query="{ tab: 'audio' }" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 012.728 2.728" /></svg>
                  Audio Badges
                </router-link>
              </li>
              <li>
                <router-link to="/settings" :query="{ tab: 'resolution' }" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                  Resolution Badges
                </router-link>
              </li>
              <li>
                <router-link to="/settings" :query="{ tab: 'review' }" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
                  Review Badges
                </router-link>
              </li>
            </ul>
            
            <div class="divider"></div>
            
            <div class="rounded-lg bg-base-200 p-4 mt-4">
              <h3 class="font-bold mb-2">System Status</h3>
              <div class="flex flex-col gap-2">
                <div class="flex justify-between">
                  <span>CPU Usage</span>
                  <span>23%</span>
                </div>
                <progress class="progress progress-primary" value="23" max="100"></progress>
                
                <div class="flex justify-between mt-2">
                  <span>Memory Usage</span>
                  <span>45%</span>
                </div>
                <progress class="progress progress-secondary" value="45" max="100"></progress>
                
                <div class="flex justify-between mt-2">
                  <span>Disk Space</span>
                  <span>78%</span>
                </div>
                <progress class="progress progress-accent" value="78" max="100"></progress>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  mounted() {
    // Add event listeners for theme switching
    document.querySelectorAll('[data-set-theme]').forEach(button => {
      button.addEventListener('click', () => {
        const theme = button.getAttribute('data-set-theme');
        document.documentElement.setAttribute('data-theme', theme);
        // Update the main container's data-theme attribute
        document.querySelector('.min-h-screen').setAttribute('data-theme', theme);
      });
    });

    // For mobile drawer: close drawer when an item is clicked
    if (window.innerWidth < 1024) { // lg breakpoint
      document.querySelectorAll('.drawer-side .menu a').forEach(menuItem => {
        menuItem.addEventListener('click', () => {
          document.getElementById('my-drawer').checked = false;
        });
      });
    }
  }
}
</script>

<style>
/* Any global styles can go here */
</style>
