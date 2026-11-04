// Quiz ML entry: loads the question bank and the progress, asks for a login on the hosted site, routes #/….
import { accountConfigured, login, session } from "../auth.js";
import { icon } from "../icons.js";
import { esc } from "../md.js";
import { backend, loadProgress, pullRemote } from "../store.js";
import { render, setBank } from "./views.js";

const app = document.getElementById("app");

function renderLogin(message = "") {
  app.innerHTML = `<main class="login"><form class="login-card" data-login>
      <div class="brand"><span class="logo">${icon("help")}</span><span>Quiz ML</span></div>
      <h1>Вход</h1>
      <p class="muted small">Аккаунт тот же, что на ML-дорожке. Ответы сохраняются в нём.</p>
      <label>Логин<input class="answer" name="user" autocomplete="username" autocapitalize="off" required></label>
      <label>Пароль<input class="answer" name="password" type="password" autocomplete="current-password" required></label>
      <div class="bad small" data-msg>${esc(message)}</div>
      <button class="btn primary big" type="submit">Войти</button>
    </form></main>`;
  app.querySelector("[data-login]").addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    const btn = e.target.querySelector("button");
    btn.disabled = true;
    btn.textContent = "Вхожу…";
    try {
      await login(String(f.get("user")), String(f.get("password")));
      await loadProgress();
      start();
    } catch (err) {
      renderLogin(err.message);
    }
  });
}

let started = false;

function start() {
  if (location.hash === "#/login") location.hash = "#/";
  render();
  if (started) return;
  started = true;
  window.addEventListener("hashchange", render);
  // Phone and laptop share the gist: a newer copy from the other device replaces this one.
  document.addEventListener("visibilitychange", async () => {
    if (document.visibilityState === "visible" && (await pullRemote())) render({ keepRound: true });
  });
}

async function main() {
  try {
    const r = await fetch("data/pyquiz.json");
    if (!r.ok) throw new Error(`data/pyquiz.json: ${r.status}`);
    setBank(await r.json());
    await loadProgress();
  } catch (err) {
    app.innerHTML = `<div class="card pad"><h2>Не удалось загрузить Quiz ML</h2><pre class="err">${esc(err.message)}</pre></div>`;
    return;
  }
  // On the hosted site the account is the only storage; locally the server works without it.
  if (!backend.server && !session() && (await accountConfigured())) return renderLogin();
  start();
}

main();

// The shortcut on the phone works offline; the worker covers quiz.html only, the rest of the site is left alone.
navigator.serviceWorker?.register("quiz-sw.js", { scope: "./quiz" }).catch((err) => console.warn("service worker", err));
