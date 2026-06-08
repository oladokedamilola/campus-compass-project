// Campus Compass - Service Worker
// Version: v2.0.0 - Authentication-aware with no HTML caching

const CACHE_NAME = "campus-compass-v2";
const DYNAMIC_CACHE = "campus-compass-dynamic-v2";

// Only cache static assets - NEVER cache HTML pages
const STATIC_ASSETS = [
  "/static/css/style.css",
  "/static/js/main.js",
  "/static/js/flash.js",
  "/static/js/notifications.js",
  "/static/js/sidebar.js",
  "/static/js/pwa.js",
  "/manifest.json"
];

// Auth pages that should NEVER be cached
const AUTH_PAGES = [
  "/",
  "/auth/login",
  "/auth/register",
  "/auth/verify-matric",
  "/auth/staff-login",
  "/auth/forgot-password",
  "/dashboard",
  "/map",
  "/locations",
  "/profile",
  "/favorites",
  "/admin"
];

// Install event - cache only static assets (NO HTML)
self.addEventListener("install", function(event) {
  console.log("[Service Worker] Installing v2...");
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log("[Service Worker] Caching static assets only");
      return cache.addAll(STATIC_ASSETS);
    }).then(function() {
      // Skip waiting to activate immediately
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches and take control
self.addEventListener("activate", function(event) {
  console.log("[Service Worker] Activating v2...");
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME && cacheName !== DYNAMIC_CACHE) {
            console.log("[Service Worker] Deleting old cache:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(function() {
      // Claim all clients immediately
      return self.clients.claim();
    })
  );
});

// Helper to check if URL should be cached
function shouldCache(url) {
  // Never cache HTML pages
  if (url.pathname === '/' || url.pathname.endsWith('.html')) {
    return false;
  }
  
  // Never cache auth pages or dashboard pages
  for (const page of AUTH_PAGES) {
    if (url.pathname === page || url.pathname.startsWith(page + '/')) {
      return false;
    }
  }
  
  // Only cache static assets with extensions
  const cacheableExtensions = ['.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp'];
  return cacheableExtensions.some(ext => url.pathname.endsWith(ext));
}

// Fetch event - NETWORK FIRST for HTML, CACHE FIRST for static assets
self.addEventListener("fetch", function(event) {
  const url = new URL(event.request.url);
  
  // Skip cross-origin requests
  if (url.origin !== self.location.origin) {
    return;
  }
  
  // For HTML pages and auth pages - NETWORK ONLY (never use cache)
  if (!shouldCache(url)) {
    console.log("[Service Worker] Network only for:", url.pathname);
    event.respondWith(
      fetch(event.request).catch(function(error) {
        console.log("[Service Worker] Network failed for:", url.pathname, error);
        // Only return offline page for root path
        if (url.pathname === '/') {
          return caches.match('/offline');
        }
        return new Response('Network error. Please check your connection.', {
          status: 503,
          statusText: 'Service Unavailable'
        });
      })
    );
    return;
  }
  
  // For static assets - CACHE FIRST, then network
  event.respondWith(
    caches.match(event.request).then(function(cachedResponse) {
      if (cachedResponse) {
        console.log("[Service Worker] Cache hit for:", url.pathname);
        return cachedResponse;
      }
      
      console.log("[Service Worker] Network fetch for:", url.pathname);
      return fetch(event.request).then(function(networkResponse) {
        // Cache valid responses
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      });
    })
  );
});