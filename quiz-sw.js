// Quiz ML service worker: the quiz opens and works without a network.
// Network first, so a deploy is seen at once; the cache answers only when the network does not.
// Requests to other origins (the GitHub gist API) and to the local server API pass through untouched.
const CACHE = "quizml-v3";
const FILES = [
  "quiz.html", "quiz.webmanifest",
  "css/app.css", "css/quiz.css",
  "js/quiz/main.js", "js/quiz/views.js", "js/quiz/question.js", "js/quiz/answer.js",
  "js/auth.js", "js/store.js", "js/md.js", "js/icons.js", "js/leitner.js",
  "data/pyquiz.json",
  "vendor/fonts/golos-text-cyrillic-wght-normal.woff2", "vendor/fonts/golos-text-latin-wght-normal.woff2",
  "vendor/fonts/jetbrains-mono-cyrillic-wght-normal.woff2", "vendor/fonts/jetbrains-mono-latin-wght-normal.woff2",
  "img/quiz-180.png", "img/quiz-192.png", "img/quiz-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("quizml-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin || url.pathname.includes("/api/")) return;
  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok) {
          const copy = res.clone();
          e.waitUntil(caches.open(CACHE).then((c) => c.put(req, copy)));
        }
        return res;
      })
      .catch(() => caches.match(req, { ignoreSearch: true }).then((hit) => hit || Response.error())),
  );
});
