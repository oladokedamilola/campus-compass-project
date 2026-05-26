// Campus Compass - Service Worker
// Version: v1.0.0
// Enables offline functionality and PWA installation

const CACHE_NAME = 'campus-compass-v1';
const STATIC_CACHE_NAME = 'campus-compass-static-v1';
const MAP_CACHE_NAME = 'campus-compass-maps-v1';
const DATA_CACHE_NAME = 'campus-compass-data-v1';

// Core assets to cache for offline use
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/flash.js',
  '/static/js/notifications.js',
  '/static/js/sidebar.js',
  '/manifest.json',
  '/offline'
];

// Map tile patterns to cache (OpenStreetMap CartoDB Dark)
const mapTilePatterns = [
  'https://*.basemaps.cartocdn.com/dark_all/*',
  'https://*.basemaps.cartocdn.com/dark_all/*/*/*.png'
];

// Install event - cache core assets
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching core assets');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        // Skip waiting to activate immediately
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating...');
  
  const cacheWhitelist = [STATIC_CACHE_NAME, MAP_CACHE_NAME, DATA_CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Claim clients to take control immediately
      return self.clients.claim();
    })
  );
});

// Helper: Check if request is for a map tile
function isMapTileRequest(request) {
  const url = request.url;
  return url.includes('basemaps.cartocdn.com') || 
         url.includes('tile.openstreetmap.org') ||
         url.includes('cartocdn.com');
}

// Helper: Check if request is for campus data
function isDataRequest(request) {
  const url = request.url;
  return url.includes('/static/data/') || 
         url.includes('/dashboard/favorites') ||
         url.includes('/dashboard/stats');
}

// Helper: Check if request is for HTML navigation
function isHtmlRequest(request) {
  return request.mode === 'navigate' || 
         (request.method === 'GET' && request.headers.get('accept') && 
          request.headers.get('accept').includes('text/html'));
}

// Fetch event - cache-first strategy with fallbacks
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Skip non-GET requests and Chrome extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    event.respondWith(fetch(request));
    return;
  }
  
  // Handle HTML navigation requests (offline fallback)
  if (isHtmlRequest(request)) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Cache the response for offline use
          const responseClone = response.clone();
          caches.open(STATIC_CACHE_NAME).then(cache => {
            cache.put(request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // Return offline page if network fails
          return caches.match('/offline');
        })
    );
    return;
  }
  
  // Handle map tile requests - cache first, network fallback
  if (isMapTileRequest(request)) {
    event.respondWith(
      caches.open(MAP_CACHE_NAME)
        .then(cache => {
          return cache.match(request).then(cachedResponse => {
            if (cachedResponse) {
              // Return cached tile, then update in background
              fetch(request).then(networkResponse => {
                if (networkResponse && networkResponse.status === 200) {
                  cache.put(request, networkResponse.clone());
                }
              }).catch(() => {});
              return cachedResponse;
            }
            // Not in cache, fetch from network
            return fetch(request).then(networkResponse => {
              if (networkResponse && networkResponse.status === 200) {
                cache.put(request, networkResponse.clone());
              }
              return networkResponse;
            });
          });
        })
    );
    return;
  }
  
  // Handle data requests (campus_data.json) - network first, cache fallback
  if (isDataRequest(request)) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const responseClone = response.clone();
          caches.open(DATA_CACHE_NAME).then(cache => {
            cache.put(request, responseClone);
          });
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
    return;
  }
  
  // Handle static assets - cache first, network fallback
  if (url.pathname.match(/\.(css|js|json|png|jpg|jpeg|gif|svg|ico)$/)) {
    event.respondWith(
      caches.match(request)
        .then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          return fetch(request).then(networkResponse => {
            if (networkResponse && networkResponse.status === 200) {
              const responseClone = networkResponse.clone();
              caches.open(STATIC_CACHE_NAME).then(cache => {
                cache.put(request, responseClone);
              });
            }
            return networkResponse;
          });
        })
    );
    return;
  }
  
  // Default: network first with cache fallback
  event.respondWith(
    fetch(request)
      .catch(() => {
        return caches.match(request);
      })
  );
});

// Background sync for offline favorites
self.addEventListener('sync', event => {
  if (event.tag === 'sync-favorites') {
    console.log('[Service Worker] Syncing favorites...');
    event.waitUntil(syncFavorites());
  }
});

async function syncFavorites() {
  // Get pending favorites from IndexedDB
  const pendingFavorites = await getPendingFavorites();
  
  for (const favorite of pendingFavorites) {
    try {
      const response = await fetch('/dashboard/favorites/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(favorite)
      });
      
      if (response.ok) {
        await removePendingFavorite(favorite.id);
        console.log('[Service Worker] Synced favorite:', favorite.place_name);
      }
    } catch (error) {
      console.error('[Service Worker] Failed to sync favorite:', error);
    }
  }
}

// Helper functions for IndexedDB (simplified)
function getPendingFavorites() {
  return new Promise((resolve) => {
    // For now, return empty array
    // This would be implemented with actual IndexedDB
    resolve([]);
  });
}

function removePendingFavorite(id) {
  return Promise.resolve();
}