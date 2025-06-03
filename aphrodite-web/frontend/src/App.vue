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
              <p>Aphrodite © 2025</p>
            </div>
          </footer>
        </div>
      </div>

      <!-- Sidebar Content -->
      <div class="drawer-side z-10">
        <label for="my-drawer" class="drawer-overlay"></label>
        <div class="bg-base-100 w-80 min-h-screen">
          <!-- Removed green banner -->
          <div class="px-4 py-6">
            <div class="flex flex-col items-center mb-6">
              <div class="avatar">
                <div class="w-24 mask mask-squircle flex items-center justify-center">
                  <img src="/images/android-chrome-192x192.png" alt="Aphrodite logo" />
                </div>
              </div>
              <h2 class="mt-2 text-xl font-bold">Aphrodite</h2>
              <VersionChecker />
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
                <router-link to="/execute" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                  Execute
                </router-link>
              </li>
              <li>
                <router-link to="/schedules" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  Schedules
                </router-link>
              </li>
              <li>
                <router-link to="/preview" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                  Preview
                </router-link>
              </li>
              <li>
                <router-link to="/poster-manager" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                  Poster Manager
                </router-link>
              </li>
              <li>
                <router-link to="/settings" active-class="active">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                  Settings
                </router-link>
              </li>
              
              <!-- Badge Types section removed -->
            </ul>
            
            <div class="divider"></div>
            
            <!-- System Status section removed -->
            
            <!-- Footer with logos -->
            <div class="flex items-center justify-between mt-8 p-4">
              <div class="avatar">
                <div class="w-12 mask mask-squircle">
                  <img src="/images/professor_relaxing.png" alt="Avatar" />
                </div>
              </div>
              <div class="flex gap-4">
                <a href="https://github.com/jackkerouac" target="_blank" rel="noopener noreferrer">
                  <img src="/images/github.webp" alt="GitHub" class="w-8 h-8" />
                </a>
                <a href="https://ko-fi.com/jackkerouac" target="_blank" rel="noopener noreferrer">
                  <img src="/images/kofi.png" alt="Ko-fi" class="w-8 h-8" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VersionChecker from './components/VersionChecker.vue';

export default {
  name: 'App',
  components: {
    VersionChecker
  },
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
