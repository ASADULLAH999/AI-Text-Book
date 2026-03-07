/**
 * T105 — Service Worker for offline error handling.
 *
 * Strategy:
 *   - Static assets (JS/CSS/images): Cache-first (long-lived CDN assets).
 *   - Document pages (.html): Network-first with offline fallback.
 *   - API requests (/api/): Network-only; return structured error JSON on failure.
 */

const CACHE_NAME = 'ai-textbook-v1';
const OFFLINE_PAGE = '/offline.html';

// Assets to pre-cache on install
const PRECACHE_URLS = [
  '/',
  OFFLINE_PAGE,
];

// ── Install ──────────────────────────────────────────────────────────────────

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// ── Activate ─────────────────────────────────────────────────────────────────

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// ── Fetch ────────────────────────────────────────────────────────────────────

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin requests
  if (request.method !== 'GET' || url.origin !== self.location.origin) {
    return;
  }

  // API requests: network-only with structured error fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() =>
        new Response(
          JSON.stringify({
            error: 'offline',
            message: 'You appear to be offline. Please check your connection and try again.',
            code: 'NETWORK_ERROR',
          }),
          {
            status: 503,
            headers: {
              'Content-Type': 'application/json',
              'X-Offline': 'true',
            },
          }
        )
      )
    );
    return;
  }

  // Static assets (JS/CSS/fonts/images): cache-first
  if (/\.(js|css|woff2?|ttf|eot|ico|svg|png|jpg|webp|avif)$/.test(url.pathname)) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            if (response.ok) {
              const clone = response.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
            }
            return response;
          })
      )
    );
    return;
  }

  // HTML pages: network-first with offline page fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() =>
        caches.match(request).then(
          (cached) => cached || caches.match(OFFLINE_PAGE)
        )
      )
  );
});
