// Campus Compass - Service Worker
// Version: v1.0.0

const CACHE_NAME = "campus-compass-v1";

const urlsToCache = [
  "/",
  "/static/css/style.css",
  "/static/js/main.js",
  "/static/js/flash.js",
  "/static/js/notifications.js",
  "/static/js/sidebar.js",
  "/static/js/pwa.js",
  "/manifest.json",
  "/offline"
];

// Install event - cache core assets
self.addEventListener("install", function(event) {
  console.log("[Service Worker] Installing...");
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log("[Service Worker] Caching core assets");
      return cache.addAll(urlsToCache);
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", function(event) {
  console.log("[Service Worker] Activating...");
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log("[Service Worker] Deleting old cache:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener("fetch", function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      // Cache hit - return response
      if (response) {
        return response;
      }
      
      // Clone the request
      var fetchRequest = event.request.clone();
      
      return fetch(fetchRequest).then(function(response) {
        // Check if valid response
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }
        
        // Clone the response
        var responseToCache = response.clone();
        
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, responseToCache);
        });
        
        return response;
      });
    })
  );
});