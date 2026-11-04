// End-to-end checks of the study app in a real browser (Chromium via Playwright).
// Run: bash app/tests/run_e2e.sh   (starts a server with a throwaway progress file)
const { chromium } = require("playwright");
const fs = require("fs");

const BASE = process.env.BASE || "http://127.0.0.1:8799";
const PROGRESS = process.env.PROGRESS_FILE;
const REFS = JSON.parse(fs.readFileSync(process.env.REFS_FILE, "utf8"));

const results = [];
async function check(name, fn) {
  const t0 = Date.now();
  try {
    await fn();
    results.push({ name, ok: true, ms: Date.now() - t0 });
    console.log(`  ✓ ${name} (${((Date.now() - t0) / 1000).toFixed(1)} с)`);
  } catch (err) {
    results.push({ name, ok: false, err: err.message });
    console.log(`  ✗ ${name}\n      ${err.message.split("\n").slice(0, 4).join("\n      ")}`);
  }
}
function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

async function setCode(page, code) {
  await page.click(".cm-content");
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Delete");
  await page.keyboard.insertText(code);
}

const guestFile = (user) => PROGRESS.replace(/progress\.json$/, `progress-${user}.json`);

async function savedProgress(ready, file = PROGRESS) {
  // The app debounces saves by 600 ms.
  let p = null;
  for (let i = 0; i < 20; i++) {
    await new Promise((r) => setTimeout(r, 250));
    if (fs.existsSync(file)) {
      p = JSON.parse(fs.readFileSync(file, "utf8"));
      if (ready(p)) return p;
    }
  }
  return p;
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 860 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));

  console.log("Playwright: сценарий понедельника 26.10");

  await check("26.10: главный экран открывает первый шаг понедельника", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/`);
    await page.waitForSelector(".stage-head h1");
    assert(await page.isVisible(".now"), "нет отметки «сейчас»");
    const h1 = await page.textContent(".stage-head h1");
    assert(h1.includes("Big-O"), `заголовок шага: ${h1}`);
    const top = await page.textContent("header.top");
    assert(top.includes("Неделя 1"), `шапка: ${top}`);
    assert((await page.$$(".week-list li")).length === 13, "в списке недель не 13 недель");
    assert(await page.$(".week-list li.cur"), "текущая неделя не выделена");
    assert((await page.$$(".panel .mod")).length === 3, "в неделе не 3 блока");
    assert((await page.$$(".panel .steps li")).length >= 20, "в блоке 1 мало шагов");
    assert((await page.$$(".step-bar .sq")).length >= 20, "в полосе шагов мало квадратиков");
    const text = await page.textContent("body");
    assert(!/[\u{1F300}-\u{1FAFF}\u2600-\u27BF]/u.test(text), "на странице есть эмодзи");
    assert(!/\d+\s?(мин|′)/.test(text), "на странице есть минуты");
  });

  await check("Теория: кнопка «Прочитал» появляется после открытия источника", async () => {
    assert(!(await page.$("[data-act=done]")), "кнопка видна до открытия источника");
    const [popup] = await Promise.all([ctx.waitForEvent("page"), page.click("[data-source]")]);
    await popup.close();
    await page.waitForSelector("[data-act=done]");
    await page.click("[data-act=done]");
    await page.waitForSelector("[data-next] a.btn.primary");
  });

  await check("«Дальше →» открывает следующий шаг: #217", async () => {
    await page.click("[data-next] a.btn.primary");
    await page.waitForSelector(".cm-content");
    assert(page.url().endsWith("#/step/w01-mon-02"), `адрес: ${page.url()}`);
    assert((await page.textContent(".stage-head h1")).includes("217"), "заголовок не #217");
  });

  await check("Pyodide: шаблон кода не проходит тесты", async () => {
    await page.click("[data-act=run]");
    await page.waitForSelector("[data-results] .verdict", { timeout: 90000 });
    assert(await page.isVisible("[data-results] .verdict.bad"), "шаблон прошёл тесты");
  });

  await check("Pyodide: неверное решение получает WA", async () => {
    await setCode(page, "class Solution:\n    def containsDuplicate(self, nums):\n        return False\n");
    await page.click("[data-act=submit]");
    await page.waitForSelector("[data-results] .verdict", { timeout: 60000 });
    const v = await page.textContent("[data-results] .verdict");
    assert(v.includes("Пройдено"), `вердикт: ${v}`);
  });

  await check("Pyodide: верное решение принято, шаг сдан, прогресс записан на диск", async () => {
    await setCode(page, REFS.lc217);
    await page.click("[data-act=submit]");
    await page.waitForSelector("[data-results] .verdict.ok", { timeout: 60000 });
    const v = await page.textContent("[data-results] .verdict.ok");
    assert(v.includes("Принято"), `вердикт: ${v}`);
    await page.waitForSelector("[data-next] a.btn.primary");
    const next = await page.getAttribute("[data-next] a.btn.primary", "href");
    assert(next === "#/step/w01-mon-03", `следующий шаг: ${next}`);
    const p = await savedProgress((x) => x.steps?.["w01-mon-02"]?.status === "done");
    assert(p?.steps?.["w01-mon-02"]?.status === "done", "в файле прогресса нет сданного шага");
    assert(p.steps["w01-mon-02"].solution?.includes("seen"), "решение не сохранено");
  });

  await check("После перезагрузки текущий шаг — №3 (прогресс восстановлен)", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/`);
    await page.waitForSelector(".stage-head h1");
    const h1 = await page.textContent(".stage-head h1");
    assert(h1.includes("изменяемость"), `заголовок: ${h1}`);
    assert((await page.$$(".panel .steps li.done")).length === 2, "отмечено не 2 шага");
  });

  await check("Квиз: вопрос «что выведет код» проверяется", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/step/w01-mon-07`);
    await page.waitForSelector(".quiz [data-q='0'] [data-input]");
    await page.fill("[data-q='0'] [data-input]", "[1, 2]");
    await page.click("[data-q='0'] [data-check]");
    await page.waitForSelector("[data-q='0'] .q-verdict.bad");
    await page.fill("[data-q='0'] [data-input]", "[1, 2, 3]");
    await page.click("[data-q='0'] [data-check]");
    await page.waitForSelector("[data-q='0'] .q-verdict.ok", { timeout: 5000 });
  });

  await check("Упражнение NumPy (softmax): numpy грузится, решение принято", async () => {
    await page.goto(`${BASE}/?today=2026-11-12#/step/w03-thu-07`);
    await page.waitForSelector(".cm-content");
    await setCode(page, REFS.softmax);
    await page.click("[data-act=submit]");
    await page.waitForSelector("[data-results] .verdict", { timeout: 120000 });
    const v = await page.textContent("[data-results] .verdict");
    assert(await page.isVisible("[data-results] .verdict.ok"), `вердикт: ${v}`);
  });

  await check("Упражнение EDA: pandas и датасет sklearn работают в браузере", async () => {
    await page.goto(`${BASE}/?today=2026-11-14#/step/w03-sat-04`);
    await page.waitForSelector(".cm-content");
    await setCode(page, REFS.eda);
    await page.click("[data-act=submit]");
    await page.waitForSelector("[data-results] .verdict", { timeout: 180000 });
    const v = await page.textContent("[data-results] .verdict");
    assert(await page.isVisible("[data-results] .verdict.ok"), `вердикт: ${v}`);
  });

  await check("Тесты на ловушки: сайт принимает проверки, которые ловят B1–B3", async () => {
    await page.goto(`${BASE}/?today=2026-10-31#/step/w01-sat-07`);
    await page.waitForSelector(".cm-content");
    await setCode(page, "def check_add(add):\n    pass\n\ndef check_grid(g):\n    pass\n\ndef check_multipliers(m):\n    pass\n\ndef check_copy(c):\n    pass\n");
    await page.click("[data-act=submit]");
    await page.waitForSelector("[data-results] .verdict", { timeout: 60000 });
    assert(await page.isVisible("[data-results] .verdict.bad"), "пустые проверки приняты");
    await setCode(page, REFS.tests);
    await page.click("[data-act=submit]");
    await page.waitForSelector("[data-results] .verdict.ok", { timeout: 60000 });
  });

  await check("Практика с полем для текста: ответ сохраняется, шаг закрывается", async () => {
    await page.goto(`${BASE}/?today=2026-11-01#/step/w01-sun-03`);
    await page.waitForSelector("[data-note]");
    assert(!(await page.$("[data-act=done]")), "кнопка закрытия видна до ответов");
    const notes = await page.$$("[data-note]");
    for (const n of notes) await n.fill("Значение по умолчанию вычисляется один раз при def.");
    await page.waitForSelector("[data-act=done]");
    await page.click("[data-act=done]");
    await page.waitForSelector("[data-next] a.btn.primary");
    const p = await savedProgress((x) => x.steps?.["w01-sun-03"]?.status === "done");
    assert(p?.notes?.["w01-sun-03:0"]?.includes("один раз"), "текст ответа не сохранён в файле прогресса");
  });

  await check("Бесконечный цикл останавливается по таймауту", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/step/w01-mon-08`);
    await page.waitForSelector(".cm-content");
    await setCode(page, "while True:\n    pass\n");
    await page.click("[data-act=submit]");
    await page.waitForSelector("[data-results] .verdict.warn", { timeout: 40000 });
    await page.waitForSelector(".dot.py-ready", { timeout: 60000 });
  });

  await check("Блоки: вкладка блока 2 открывает его первый несданный шаг", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/block/w01-b2`);
    await page.waitForSelector(".mod.open");
    assert((await page.textContent(".mod.open .mod-h")).includes("Математика"), "открыт не блок 2");
    assert((await page.$$(".mod.open .steps li")).length > 0, "в блоке 2 нет шагов");
  });

  await check("«Уже знаю» засчитывает шаг с отметкой в журнале; оценка шага сохраняется", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/step/w01-mon-04`);
    await page.click("[data-skip]");
    await page.waitForSelector("[data-next] [data-rate]");
    await page.click("[data-rate=easy]");
    await page.waitForSelector("[data-rate=easy].on");
    const p = await savedProgress((x) => x.steps?.["w01-mon-04"]?.rating === "easy");
    assert(p?.steps?.["w01-mon-04"]?.skipped === true, "нет отметки skipped");
    assert(p.events.some((e) => e.type === "skip" && e.step === "w01-mon-04"), "нет события skip в журнале");
  });

  await check("Повторение: вопросы из сданного квиза, ответ меняет коробку Лейтнера", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/review`);
    await page.waitForSelector(".review h1");
    await page.click("[data-extra], [data-start]");
    await page.waitForSelector("[data-card]");
    await page.click("[data-dunno]");
    await page.waitForSelector("[data-next]");
    const p = await savedProgress((x) => Object.keys(x.review || {}).length > 0);
    const cards = Object.values(p.review);
    assert(cards.some((c) => c.wrong === 1 && c.box === 0), JSON.stringify(cards));
  });

  await check("Anki на сайте: карточки по темам дня, 15 новых в день, сессия сдаёт шаг", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/step/w01-mon-10`);
    await page.waitForSelector("[data-anki-start]");
    const stats = await page.textContent(".anki-stats");
    assert(stats.includes(`0 из ${REFS.ankiDay1}`), `по темам 26.10 не ${REFS.ankiDay1} карточек: ${stats}`);
    assert((await page.textContent("[data-anki-start]")).includes("(15)"), "в сессии не 15 новых карточек");
    await page.click("[data-anki-start]");
    // The first card by keyboard (Space shows the answer, 2 = "Хорошо"), the second "again": it comes back at the end.
    await page.waitForSelector(".anki-face");
    await page.keyboard.press(" ");
    await page.waitForSelector("[data-grade]");
    assert((await page.$$(".anki-back")).length === 1, "оборот карточки не показан");
    await page.keyboard.press("2");
    await page.click("[data-reveal]");
    await page.click("[data-grade=again]");
    let total = "";
    for (let i = 0; i < 40 && !(await page.$(".callout.ok")); i++) {
      total = await page.textContent(".review-top");
      await page.click("[data-reveal]");
      await page.click("[data-grade=good]");
    }
    assert(total.includes("/ 16"), `карточка «Снова» не вернулась в сессию: ${total}`);
    await page.waitForSelector("[data-next] a.btn.primary");
    const p = await savedProgress((x) => x.steps?.["w01-mon-10"]?.status === "done");
    assert(p?.steps?.["w01-mon-10"]?.status === "done", "шаг Anki не сдан");
    const anki = Object.entries(p.review).filter(([k]) => k.startsWith("a:"));
    assert(anki.length === 15, `в коробках ${anki.length} карточек Anki, а не 15`);
    assert(anki.filter(([, c]) => c.wrong === 1).length === 1, "нет карточки с ответом «Снова»");
    assert((await page.textContent(".anki-stats")).includes(`15 из ${REFS.ankiDay1}`), "счётчик изученных не 15");
  });

  await check("Anki: шаг недели 3 даёт новые карточки только по темам до своего дня", async () => {
    const cards = (await (await fetch(`${BASE}/data/anki.json`)).json()).cards;
    const byId = new Map(cards.map((c) => [c.id, c]));
    // Everything up to Monday 09.11 is already learned: Tuesday's step (10.11) must bring only cards of 10.11.
    const review = {};
    for (const c of cards.filter((c) => c.day <= "2026-11-09")) {
      review[`a:${c.id}`] = { box: 3, due: Date.now() + 10 * 86400000, seen: 1, wrong: 0, intro: "2026-11-01" };
    }
    const start = { version: 1, steps: {}, code: {}, quiz: {}, checklist: {}, notes: {}, review, events: [] };
    const ctx5 = await browser.newContext();
    await ctx5.route("**/api/progress*", (r) => r.request().method() === "POST" ? r.fulfill({ json: { ok: true } }) : r.fulfill({ json: start }));
    const ap = await ctx5.newPage();
    await ap.goto(`${BASE}/?today=2026-11-10#/step/w03-tue-08`);
    await ap.waitForSelector("[data-anki-start]");
    const want = cards.filter((c) => c.day === "2026-11-10").length;
    const stats = await ap.textContent(".anki-stats");
    assert(stats.includes(`из ${REFS.ankiWeek3Wed}`), `по темам до 10.11 не ${REFS.ankiWeek3Wed} карточек: ${stats}`);
    // More than 15 cards that day: "Ещё 10 новых" takes them all.
    await ap.click(want > 15 ? "[data-anki-more]" : "[data-anki-start]");
    const seen = [];
    while (!(await ap.$(".callout.ok"))) {
      seen.push(await ap.getAttribute(".anki-face", "data-card-id"));
      await ap.click("[data-reveal]");
      await ap.click("[data-grade=good]");
    }
    const days = [...new Set(seen.map((id) => byId.get(id)?.day))];
    assert(seen.length === want, `в сессии ${seen.length} карточек, а тем 10.11 — ${want}`);
    assert(days.length === 1 && days[0] === "2026-11-10", `пришли карточки дней ${days}`);
    await ctx5.close();
  });

  await check("Повторение задачи: условие без названия, похожие варианты, «Решить заново» с тестами", async () => {
    const ctx4 = await browser.newContext({ viewport: { width: 1280, height: 860 } });
    const posted = [];
    // Only #217 is solved: the session is exactly one problem card.
    const start = { version: 1, steps: { "w01-mon-02": { status: "done", solution: REFS.lc217 } }, code: {}, quiz: {}, checklist: {}, notes: {}, review: {}, events: [] };
    await ctx4.route("**/api/progress*", (r) => r.request().method() === "POST"
      ? (posted.push(JSON.parse(r.request().postData())), r.fulfill({ json: { ok: true } }))
      : r.fulfill({ json: start }));
    const rp = await ctx4.newPage();
    rp.on("pageerror", (e) => errors.push(e.message));
    await rp.goto(`${BASE}/?today=2026-10-26#/review`);
    await rp.click("[data-start]");
    await rp.waitForSelector(".review-problem [data-card]");
    const face = await rp.textContent("[data-card]");
    assert(face.includes("два раза или больше"), `нет условия задачи: ${face.slice(0, 120)}`);
    assert(!face.includes("217") && !face.includes("Есть ли повтор"), "в карточке видно номер или название задачи");
    await rp.click("[data-choices]");
    const options = await rp.$$eval(".option", (els) => els.map((e) => e.textContent.trim()));
    assert(options.length === 4 && options.includes("хэш-множество"), `варианты: ${options}`);
    const wrong = options.filter((o) => o !== "хэш-множество");
    assert(!wrong.some((o) => /хэш|словар|set/.test(o)), `среди неверных вариантов есть тоже верный приём: ${wrong}`);
    assert(!wrong.some((o) => /проектирование класса|связный список|дерево|сетка/.test(o)), `вариант для другого входа: ${wrong}`);
    await rp.click("[data-dunno]");
    await rp.waitForSelector(".review-actions .btn.primary[data-resolve-open]");
    assert((await rp.textContent("[data-verdict]")).includes("хэш-множество"), "ответ не показан");
    await rp.click("[data-resolve-open]");
    await rp.waitForSelector(".resolve .cm-content");
    await setCode(rp, "class Solution:\n    def containsDuplicate(self, nums):\n        return False\n");
    await rp.click("[data-resolve-run]");
    await rp.waitForSelector("[data-resolve-out] .verdict", { timeout: 90000 });
    assert(await rp.isVisible("[data-resolve-out] .verdict.bad"), "неверное решение принято");
    await setCode(rp, REFS.lc217);
    await rp.click("[data-resolve-run]");
    await rp.waitForSelector("[data-resolve-out] .verdict.ok", { timeout: 60000 });
    await rp.waitForTimeout(1200);
    const last = posted.at(-1);
    assert(last?.review?.["p:217"]?.wrong === 1 && last.review["p:217"].box === 0, `коробка задачи: ${JSON.stringify(last?.review)}`);
    assert(last.events.some((e) => e.type === "resolve" && e.passed === e.total), "нет события решённой заново задачи");
    await rp.screenshot({ path: `${process.env.SHOTS}/review-problem.png`, fullPage: true });
    await ctx4.close();
  });

  await check("Визуализатор: кадры, объекты, стрелки и вывод по шагам", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/tutor`);
    await page.click("[data-act=sample]");
    await page.click("[data-act=trace]");
    await page.waitForSelector(".tutor .tu-frame", { timeout: 60000 });
    let maxFrames = 0;
    while (await page.isEnabled("[data-go=next]")) {
      await page.click("[data-go=next]");
      maxFrames = Math.max(maxFrames, (await page.$$(".tu-frame")).length);
    }
    assert(maxFrames === 2, `вызов функции не показан отдельным кадром (кадров: ${maxFrames})`);
    assert((await page.textContent("[data-out]")).includes("[1, 2] [1, 2] True"), "вывод программы не тот");
    await page.waitForTimeout(100);
    assert((await page.$$(".tu-arrows path[marker-end]")).length >= 3, "нет стрелок от имён к объектам");
    assert((await page.$$(".tu-obj")).length >= 2, "нет объектов");
    await page.keyboard.press("ArrowLeft");
    assert(!(await page.textContent("[data-count]")).startsWith("Шаг 1 "), "стрелка влево не листает");
    await page.screenshot({ path: `${process.env.SHOTS}/tutor.png`, fullPage: true });
  });

  await check("«По шагам» в задаче: решение запускается на тесте 1", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/step/w01-mon-02`);
    await page.waitForSelector(".cm-content");
    await page.click("[data-act=trace]");
    await page.waitForSelector("dialog.tutor-dlg .tu-frame", { timeout: 60000 });
    assert((await page.textContent("dialog.tutor-dlg")).includes("containsDuplicate([1, 2, 3, 1])"), "нет вызова на тесте 1");
    await page.click("[data-go=last]");
    assert((await page.textContent("[data-event]")).includes("Возврат"), "последний шаг — не возврат из метода");
    await page.keyboard.press("Escape");
    await page.waitForSelector("dialog.tutor-dlg", { state: "detached" });
  });

  await check("Панель шагов сворачивается и помнит это после перезагрузки", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/`);
    await page.click("[data-collapse]");
    assert(await page.$("aside.panel.collapsed"), "панель не свернулась");
    await page.reload();
    await page.waitForSelector("aside.panel");
    assert(await page.$("aside.panel.collapsed"), "свёрнутость не запомнилась");
    await page.click("[data-collapse]");
  });

  await check("Вход: неверный пароль отклонён, верный пускает (пароль из TEST_PASS)", async () => {
    const ctx2 = await browser.newContext();
    // The decrypted token is real: keep test events out of the account gist.
    await ctx2.route("https://api.github.com/**", (r) => r.abort());
    const lp = await ctx2.newPage();
    await lp.goto(`${BASE}/#/login`);
    await lp.fill("[name=user]", "fafakaj");
    await lp.fill("[name=password]", "wrong-password");
    await lp.click("[data-login] button");
    await lp.waitForSelector("[data-msg]:not(:empty)", { timeout: 20000 });
    assert((await lp.textContent("[data-msg]")).includes("Неверный"), "нет сообщения об ошибке");
    if (process.env.TEST_PASS) {
      await lp.fill("[name=user]", "fafakaj");
      await lp.fill("[name=password]", process.env.TEST_PASS);
      await lp.click("[data-login] button");
      await lp.waitForSelector("[data-logout]", { timeout: 20000 });
      assert((await lp.textContent("[data-logout]")).includes("fafakaj"), "имя не в шапке");
    }
    await ctx2.close();
  });

  for (const [user, pass] of [["smetanka", process.env.TEST_PASS_GUEST], ["keshapticya", process.env.TEST_PASS_KESHA], ["ir630", process.env.TEST_PASS_IR630]]) {
    await check(`Аккаунт ${user}: вход, свой прогресс, отдельный от владельца и других`, async () => {
      if (!pass) throw new Error(`нет пароля в окружении для ${user}`);
      const ctx3 = await browser.newContext();
      await ctx3.route("https://api.github.com/**", (r) => r.abort());
      const gp = await ctx3.newPage();
      await gp.goto(`${BASE}/?today=2026-10-26#/login`);
      await gp.fill("[name=user]", user);
      await gp.fill("[name=password]", pass);
      await gp.click("[data-login] button");
      await gp.waitForSelector(".stage-head h1", { timeout: 20000 });
      assert((await gp.textContent("[data-logout]")).includes(user), "имя не в шапке");
      const before = fs.existsSync(guestFile(user)) ? JSON.parse(fs.readFileSync(guestFile(user), "utf8")) : { steps: {} };
      assert(!Object.keys(before.steps).length, "у нового аккаунта уже есть сданные шаги");
      const id = await gp.$eval(".step-bar .sq.cur", (a) => a.getAttribute("href").split("/").pop());
      await gp.click("[data-skip]");
      const mine = await savedProgress((p) => p.steps[id]?.skipped, guestFile(user));
      assert(mine?.steps[id]?.skipped, `прогресс ${user} не сохранился в его файл`);
      const owner = JSON.parse(fs.readFileSync(PROGRESS, "utf8"));
      assert(!owner.steps[id]?.skipped, `пропуск ${user} попал в прогресс владельца`);
      for (const other of ["smetanka", "keshapticya", "ir630"].filter((u) => u !== user && fs.existsSync(guestFile(u)))) {
        const o = JSON.parse(fs.readFileSync(guestFile(other), "utf8"));
        assert(o.events.filter((e) => e.type === "skip").length <= 1, `пропуск ${user} попал в прогресс ${other}`);
      }
      await ctx3.close();
    });
  }

  for (const [w, h] of [[390, 844], [360, 740]]) {
    await check(`Ширина ${w} px: нет горизонтальной прокрутки (главный экран, задача, квиз, карта)`, async () => {
      const m = await browser.newPage({ viewport: { width: w, height: h } });
      for (const route of ["#/", "#/step/w01-mon-02", "#/step/w01-mon-07", "#/step/w01-mon-10", "#/map", "#/review", "#/tutor", "#/block/w01-b3"]) {
        await m.goto(`${BASE}/?today=2026-10-26${route}`);
        await m.waitForSelector("header.top");
        await m.waitForTimeout(300);
        const over = await m.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        assert(over <= 0, `${route}: страница шире экрана на ${over} px`);
      }
      await m.screenshot({ path: `${process.env.SHOTS}/phone-${w}.png`, fullPage: false });
      await m.close();
    });
  }

  await check("Месяц 1: каждый шаг недель 1–4 открывается и показывает содержимое", async () => {
    const plan = await (await fetch(`${BASE}/data/plan.json`)).json();
    const ids = plan.weeks.slice(0, 4).flatMap((w) => w.days.flatMap((d) => d.steps.map((s) => s.id)));
    const empty = [];
    for (const id of ids) {
      await page.goto(`${BASE}/?today=2026-10-26#/step/${id}`);
      await page.waitForSelector("[data-body] > *", { timeout: 5000 }).catch(() => empty.push(id));
    }
    assert(ids.length > 100, `шагов всего ${ids.length}`);
    assert(empty.length === 0, `пустые шаги: ${empty.join(", ")}`);
  });

  await check("Переводы: каждая статья #/read/ открывается, разметка разобрана, на 360 px нет прокрутки", async () => {
    const sources = await (await fetch(`${BASE}/data/sources.json`)).json();
    const slugs = [...new Set(sources.topics.flatMap((t) => t.sources).filter((s) => s.url.startsWith("#/read/")).map((s) => s.url.slice(7)))];
    assert(slugs.length >= 26, `переводов ${slugs.length}`);
    const m = await browser.newPage({ viewport: { width: 360, height: 740 } });
    m.on("pageerror", (e) => errors.push(e.message));
    for (const slug of slugs) {
      await m.goto(`${BASE}/?today=2026-10-26#/read/${slug}`);
      await m.waitForSelector(".article-body", { timeout: 5000 });
      // Code blocks keep their text as is (pytest output starts lines with "> "), so check the rest.
      const text = await m.evaluate(() => [...document.querySelectorAll(".article-body > :not(pre)")].map((e) => e.innerText).join("\n"));
      assert(!/(^|\n)\s*(#{2,4} |\|---|```|> )/.test(text), `${slug}: в тексте осталась разметка Markdown`);
      assert(await m.$(".article-head a[href^='http']"), `${slug}: нет ссылки на оригинал`);
      const over = await m.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      assert(over <= 0, `${slug}: страница шире экрана на ${over} px`);
    }
    await m.goto(`${BASE}/?today=2026-10-26#/read/python-time-complexity`);
    await m.waitForSelector(".article-body table");
    await m.screenshot({ path: `${process.env.SHOTS}/article-360.png`, fullPage: false });
    await m.close();
  });

  // ---------------------------------------------------------------- Quiz ML (phone 390×844)
  const BANK = JSON.parse(fs.readFileSync(`${__dirname}/../data/pyquiz.json`, "utf8"));
  const Q = new Map(BANK.questions.map((q) => [q.id, q]));
  const qz = await (await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true })).newPage();
  qz.on("pageerror", (e) => errors.push(`quiz: ${e.message}`));
  const qzOpen = async (hash, sel) => {
    await qz.goto(`${BASE}/quiz.html${hash}`);
    await qz.waitForSelector(sel);
  };
  /** Answers the question on screen, right or wrong; returns its id. */
  const qzAnswer = async (right) => {
    const id = await qz.getAttribute(".qz-stage", "data-qid");
    const q = Q.get(id);
    if (q.type === "input") {
      await qz.fill(".qz-input input", right ? q.answer[0] : "nosuchmethod");
      await qz.click(".qz-input button");
    } else {
      await qz.click(`[data-pick="${right ? q.answer : (q.answer + 1) % q.options.length}"]`);
    }
    await qz.waitForSelector(".qz-sheet");
    return id;
  };
  /** Plays a round to the results; `wrongFirst` answers the first question wrong. Returns the ids in order. */
  const qzRound = async (n, { wrongFirst = false } = {}) => {
    const ids = [];
    for (let i = 0; i < n; i++) {
      await qz.waitForSelector(`.qz-count:text("${i + 1} из ${n}")`);
      ids.push(await qzAnswer(!(wrongFirst && i === 0)));
      await qz.click(".qz-next .btn");
    }
    await qz.waitForSelector(".qz-score");
    return ids;
  };
  const plainMd = (s) => s.replace(/`([^`]*)`/g, "$1").replace(/\*\*?([^*]+)\*\*?/g, "$1");

  await check("Quiz ML: ссылка в шапке сайта; «Случайные 10» дают 10 разных вопросов темы и итог", async () => {
    await page.goto(`${BASE}/?today=2026-10-26#/`);
    assert(await page.$('header.top a[href="quiz.html"]'), "в шапке нет ссылки на Quiz ML");
    await qzOpen("#/topic/list-o", "[data-mode=random]");
    await qz.click("[data-mode=random]");
    const ids = await qzRound(10);
    assert(new Set(ids).size === 10, `повторы в раунде: ${ids}`);
    assert(ids.every((id) => Q.get(id).topic === "list-o"), `вопрос не из темы: ${ids}`);
    assert((await qz.textContent(".qz-score")).trim() === "10 из 10", "счёт не 10 из 10");
    await qz.click(".qz-list a >> nth=0");
    await qz.waitForSelector('.qz-sheet[data-verdict="ok"]');
    await qzOpen(`#/catalog/list-o`, ".qz-cat");
    await qz.click(`.qz-cat[data-qid="${ids[0]}"]`);
    await qz.waitForSelector(".qz-opt");
    assert(!(await qz.$(".qz-sheet")) && (await qz.isEnabled(".qz-opt >> nth=0")), "вопрос из каталога открылся уже отвеченным");
  });

  await check("Quiz ML: ошибка в «Умных 10» ставит этот вопрос первым в следующем раунде", async () => {
    await qzOpen("#/topic/dict-o", "[data-mode=smart]");
    await qz.click("[data-mode=smart]");
    const [missed] = await qzRound(10, { wrongFirst: true });
    await qz.click("[data-again]");
    await qz.waitForSelector(".qz-count");
    const first = await qz.getAttribute(".qz-stage", "data-qid");
    assert(first === missed, `первым ${first}, а ошибка была в ${missed}`);
  });

  await check("Quiz ML: неверный ответ показывает разбор выбранного варианта; ввод str.RSPLIT() засчитан", async () => {
    const q = BANK.questions.find((x) => x.type === "choice" && x.options.length === 4 && x.topic === "set-o");
    await qzOpen(`#/q/${q.id}`, ".qz-opt");
    const k = (q.answer + 2) % 4;
    await qz.click(`[data-pick="${k}"]`);
    await qz.waitForSelector("[data-mistake]");
    const shown = (await qz.textContent("[data-mistake]")).replace(/\s+/g, " ");
    const want = plainMd(q.wrong[String(k)]).replace(/\s+/g, " ").slice(0, 40);
    assert(shown.includes(want), `«В чём ошибка» не для варианта ${k}: ${shown.slice(0, 80)}`);
    await qz.click(".qz-all summary");
    assert((await qz.$$(".qz-all li")).length === 2, "в «Разборе всех вариантов» не 2 остальных варианта");
    await qzOpen("#/q/str-m-rsplit", ".qz-input input");
    await qz.fill(".qz-input input", " str.RSPLIT() ");
    await qz.click(".qz-input button");
    assert((await qz.getAttribute(".qz-sheet", "data-verdict")) === "ok", "str.RSPLIT() не засчитан");
  });

  await check("Quiz ML: двойное касание варианта записывает ответ один раз", async () => {
    const q = BANK.questions.find((x) => x.type === "choice" && x.topic === "conc-theory");
    await qzOpen(`#/q/${q.id}`, ".qz-opt");
    await qz.dblclick(`[data-pick="${q.answer}"]`);
    const p = await savedProgress((x) => x.pyquiz?.[q.id]);
    assert(p?.pyquiz?.[q.id]?.seen === 1, `seen = ${p?.pyquiz?.[q.id]?.seen}`);
    assert(p.pyquiz[q.id].box === 1 && p.pyquiz[q.id].last === "ok", JSON.stringify(p.pyquiz[q.id]));
  });

  await check("Quiz ML: каталог — все вопросы темы, статус после ответа, статус после перезагрузки", async () => {
    const n = BANK.questions.filter((x) => x.topic === "set-m").length;
    await qzOpen("#/catalog/set-m", ".qz-cat");
    assert((await qz.$$(".qz-cat")).length === n, `в каталоге не ${n} строк`);
    const first = await qz.getAttribute(".qz-cat >> nth=0", "data-qid");
    assert(await qz.$(`.qz-cat.is-new[data-qid="${first}"]`), "первый вопрос не «не решал»");
    await qz.click(".qz-cat >> nth=0");
    await qz.waitForSelector(".qz-stage");
    await qzAnswer(false);
    await qz.click(".qz-back");
    await qz.waitForSelector(`.qz-cat.is-bad[data-qid="${first}"]`);
    await savedProgress((x) => x.pyquiz?.[first]);
    await qz.reload();
    await qz.waitForSelector(`.qz-cat.is-bad[data-qid="${first}"]`, { timeout: 5000 });
    assert((await qz.textContent(`.qz-cat[data-qid="${first}"] small`)).includes("коробка 0"), "нет номера коробки");
  });

  await check("Quiz ML: «Свой набор» из двух тем — 20 вопросов только из них, выбор запомнен", async () => {
    await qzOpen("#/custom", ".qz-check");
    await qz.evaluate(() => localStorage.removeItem("quizml-custom"));
    await qz.reload();
    await qz.waitForSelector(".qz-check");
    await qz.check('.qz-check input[value="str-o"]');
    await qz.check('.qz-check input[value="conc-pick"]');
    assert((await qz.textContent("[data-start]")).includes("20 вопросов"), "кнопка не «20 вопросов»");
    await qz.click("[data-start]");
    const ids = await qzRound(20);
    assert(new Set(ids).size === 20, "повторы в своём наборе");
    const topics = new Set(ids.map((id) => Q.get(id).topic));
    assert([...topics].every((t) => t === "str-o" || t === "conc-pick"), `чужие темы: ${[...topics]}`);
    await qzOpen("#/custom", ".qz-check");
    const checked = await qz.$$eval(".qz-check input:checked", (els) => els.map((e) => e.value).sort());
    assert(checked.join() === "conc-pick,str-o", `запомнен выбор ${checked}`);
  });

  await check("Quiz ML: прогресс без ключа pyquiz (старая копия) не ломает страницу", async () => {
    // Let the last debounced save of the round land first, then leave the page so nothing writes over the edit.
    await qz.waitForTimeout(1500);
    await qz.goto("about:blank");
    const p = JSON.parse(fs.readFileSync(PROGRESS, "utf8"));
    delete p.pyquiz;
    p.saved_at = new Date(Date.now() + 60000).toISOString();
    fs.writeFileSync(PROGRESS, JSON.stringify(p));
    await qzOpen("#/", ".qz-row");
    assert((await qz.textContent(".qz-row")).includes("верно 0 из"), "счётчик темы не обнулён");
    await qzOpen("#/q/str-m-rsplit", ".qz-input input");
    await qzAnswer(true);
    const saved = await savedProgress((x) => x.pyquiz?.["str-m-rsplit"]);
    assert(saved?.pyquiz?.["str-m-rsplit"]?.last === "ok", "ответ не записан в pyquiz");
    assert(Object.keys(saved.steps).length === Object.keys(p.steps).length, "потерялись шаги сайта");
  });

  await check("Quiz ML: ярлык ставится (нет ошибок установки), без сети раунд проходится", async () => {
    const octx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true });
    const o = await octx.newPage();
    o.on("pageerror", (e) => errors.push(`quiz offline: ${e.message}`));
    await o.goto(`${BASE}/quiz.html#/`);
    await o.waitForSelector(".qz-row");
    await o.evaluate(() => navigator.serviceWorker.ready);
    const cdp = await octx.newCDPSession(o);
    const { installabilityErrors } = await cdp.send("Page.getInstallabilityErrors");
    assert(installabilityErrors.length === 0, `ошибки установки: ${JSON.stringify(installabilityErrors)}`);
    assert(await o.evaluate(() => Boolean(navigator.serviceWorker.controller)), "service worker не управляет страницей");
    await octx.setOffline(true);
    await o.reload();
    await o.waitForSelector(".qz-row", { timeout: 8000 });
    await o.goto(`${BASE}/quiz.html#/topic/code`);
    await o.click("[data-mode=random]");
    for (let i = 0; i < 10; i++) {
      await o.waitForSelector(`.qz-count:text("${i + 1} из 10")`);
      await o.click(".qz-opt >> nth=0");
      await o.click(".qz-next .btn");
    }
    await o.waitForSelector(".qz-score");
    const kept = await o.evaluate(() => Object.keys(JSON.parse(localStorage.getItem("path-progress-backup")).pyquiz).length);
    assert(kept >= 10, `без сети в копию браузера записано ${kept} ответов`);
    await octx.close();
  });

  await check("Нет ошибок JavaScript на странице", async () => {
    assert(errors.length === 0, errors.join("\n"));
  });

  await page.goto(`${BASE}/?today=2026-10-26#/`);
  await page.waitForSelector(".stage-head h1");
  await page.screenshot({ path: `${process.env.SHOTS}/desktop-now.png` });

  await browser.close();
  const bad = results.filter((r) => !r.ok);
  console.log(`\nИтог: ${results.length - bad.length} из ${results.length} проверок прошли`);
  process.exit(bad.length ? 1 : 0);
})();
