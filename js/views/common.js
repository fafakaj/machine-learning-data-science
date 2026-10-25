import { esc, md } from "../md.js";

export function sourceCard(src, { big = false } = {}) {
  if (!src) return "";
  return `<a class="source ${big ? "big" : ""}" href="${esc(src.url)}" target="_blank" rel="noopener" data-source>
      <div class="source-title">${esc(src.title)}${src.lang === "en" ? ' <span class="tag lang-en">EN</span>' : ""}</div>
      ${src.section ? `<div class="source-section">${esc(src.section)}</div>` : ""}
    </a>`;
}

export function goalsList(goals) {
  if (!goals?.length) return "";
  return `<ul class="goals">${goals.map((g) => `<li>${md(g)}</li>`).join("")}</ul>`;
}
