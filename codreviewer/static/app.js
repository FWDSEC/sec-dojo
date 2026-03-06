const LANGUAGE_CONFIG = {
  cpp: { label: "C++", hljs: "cpp" },
  python: { label: "Python", hljs: "python" },
  java: { label: "Java", hljs: "java" },
  typescript: { label: "TypeScript", hljs: "typescript" },
};

function isRevealMode() {
  const v = new URLSearchParams(window.location.search).get("reveal");
  if (!v) return false;
  return ["1", "true", "yes", "on"].includes(v.trim().toLowerCase());
}

function getStored(key, fallback) {
  try {
    const v = window.localStorage.getItem(key);
    return v ?? fallback;
  } catch {
    return fallback;
  }
}

function setStored(key, value) {
  try {
    window.localStorage.setItem(key, String(value));
  } catch {
    // ignore
  }
}

function showToast(message) {
  const el = document.getElementById("toast");
  if (!el) return;

  el.textContent = message;
  el.classList.add("show");

  window.clearTimeout(showToast._t);
  showToast._t = window.setTimeout(() => el.classList.remove("show"), 1100);
}
showToast._t = 0;

function setActiveChallengeButton(challengeId) {
  document.querySelectorAll(".challenge-item").forEach((btn) => {
    const id = Number(btn.dataset.challengeId);
    btn.classList.toggle("active", id === challengeId);
  });
}

function setActiveLangTab(lang) {
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === lang);
  });
}

function renderChallenge(challenge) {
  const kicker = document.getElementById("challenge-kicker");
  const heading = document.getElementById("challenge-heading");
  const desc = document.getElementById("challenge-description");

  if (kicker) kicker.textContent = `Challenge #${challenge.id}`;
  if (heading) heading.textContent = `${challenge.title}`;
  if (desc) desc.textContent = challenge.description ?? "";
}

function renderCode(challenge, lang) {
  const label = document.getElementById("code-lang-label");
  const codeEl = document.getElementById("code-block");
  if (!codeEl) return;

  const cfg = LANGUAGE_CONFIG[lang] ?? { label: lang, hljs: lang };
  const snippet = challenge?.snippets?.[lang] ?? "";

  if (label) label.textContent = cfg.label;

  codeEl.className = `language-${cfg.hljs}`;
  codeEl.removeAttribute("data-highlighted");
  codeEl.textContent = snippet;

  if (window.hljs) {
    window.hljs.highlightElement(codeEl);
  }
}

function wrapCodeLines(codeEl) {
  const html = codeEl.innerHTML;
  const lines = html.split("\n");
  const wrapped = lines
    .map((line, i) => {
      const safe = line.length ? line : "\u200b";
      return `<span class="code-line" data-line="${i + 1}">${safe}</span>`;
    })
    .join("");
  codeEl.innerHTML = wrapped;
}

function clearLineHighlights(codeEl) {
  codeEl.querySelectorAll(".code-line.issue, .code-line.issue-focus").forEach((el) => {
    el.classList.remove("issue", "issue-focus");
  });
}

function applyLineHighlights(codeEl, issues) {
  clearLineHighlights(codeEl);
  const lineSet = new Set();
  (issues ?? []).forEach((issue) => {
    (issue.lines ?? []).forEach((n) => {
      if (Number.isFinite(n)) lineSet.add(Number(n));
    });
  });
  lineSet.forEach((n) => {
    const el = codeEl.querySelector(`.code-line[data-line="${n}"]`);
    if (el) el.classList.add("issue");
  });
}

async function fetchChallenge(challengeId) {
  const res = await fetch(`/api/challenges/${challengeId}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

async function fetchAnswers(challengeId) {
  const res = await fetch(`/api/challenges/${challengeId}/answers?reveal=true`);
  if (!res.ok) return null;
  return await res.json();
}

function renderAnswersPanel(issues, lang) {
  const panel = document.getElementById("answers-panel");
  const list = document.getElementById("answers-list");
  if (!panel || !list) return;

  panel.hidden = false;
  list.innerHTML = "";

  const cfg = LANGUAGE_CONFIG[lang] ?? { label: lang };
  const header = document.createElement("div");
  header.className = "answers-lang";
  header.textContent = `Language: ${cfg.label}`;
  list.appendChild(header);

  if (!issues || issues.length === 0) {
    const empty = document.createElement("div");
    empty.className = "answers-empty";
    empty.textContent = "No answers available for this challenge/language.";
    list.appendChild(empty);
    return;
  }

  issues.forEach((issue) => {
    const item = document.createElement("div");
    item.className = "issue-item";

    const titleRow = document.createElement("div");
    titleRow.className = "issue-title-row";

    const title = document.createElement("div");
    title.className = "issue-title";
    title.textContent = issue.title ?? "Issue";

    const meta = document.createElement("div");
    meta.className = "issue-meta";
    const lines = Array.isArray(issue.lines) ? issue.lines.filter((n) => Number.isFinite(n)) : [];
    meta.textContent = lines.length ? `Lines: ${lines.join(", ")}` : "";

    titleRow.appendChild(title);
    if (meta.textContent) titleRow.appendChild(meta);

    const problem = document.createElement("div");
    problem.className = "issue-problem";
    problem.textContent = issue.problem ?? "";

    const fix = document.createElement("div");
    fix.className = "issue-fix";
    fix.textContent = issue.fix ?? "";

    item.appendChild(titleRow);
    if (problem.textContent) item.appendChild(problem);
    if (fix.textContent) item.appendChild(fix);

    item.addEventListener("click", () => {
      const first = lines[0];
      if (!first) return;
      const codeEl = document.getElementById("code-block");
      const target = codeEl?.querySelector(`.code-line[data-line="${first}"]`);
      if (!target) return;
      target.classList.add("issue-focus");
      target.scrollIntoView({ block: "center", behavior: "smooth" });
      window.setTimeout(() => target.classList.remove("issue-focus"), 900);
    });

    list.appendChild(item);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const challenges = window.__CHALLENGES__ ?? [];
  const initial = window.__INITIAL_CHALLENGE__;

  let currentChallenge = initial;
  let selectedLang = getStored("cr_lang", "python");
  const reveal = isRevealMode();
  let currentAnswers = null;

  if (reveal) {
    document.body.classList.add("reveal-on");
    const panel = document.getElementById("answers-panel");
    if (panel) panel.hidden = false;
  }

  if (!(selectedLang in LANGUAGE_CONFIG)) selectedLang = "python";
  setActiveLangTab(selectedLang);

  renderChallenge(currentChallenge);
  renderCode(currentChallenge, selectedLang);
  setActiveChallengeButton(currentChallenge.id);

  if (reveal) {
    const codeEl = document.getElementById("code-block");
    if (codeEl) wrapCodeLines(codeEl);
    currentAnswers = await fetchAnswers(currentChallenge.id);
    const issues = currentAnswers?.languages?.[selectedLang] ?? [];
    if (codeEl) applyLineHighlights(codeEl, issues);
    renderAnswersPanel(issues, selectedLang);
  }

  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      const lang = btn.dataset.lang;
      if (!lang || lang === selectedLang) return;
      selectedLang = lang;
      setStored("cr_lang", selectedLang);
      setActiveLangTab(selectedLang);
      renderCode(currentChallenge, selectedLang);

      if (reveal) {
        const codeEl = document.getElementById("code-block");
        if (codeEl) wrapCodeLines(codeEl);
        const issues = currentAnswers?.languages?.[selectedLang] ?? [];
        if (codeEl) applyLineHighlights(codeEl, issues);
        renderAnswersPanel(issues, selectedLang);
      }
    });
  });

  document.querySelectorAll(".challenge-item").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = Number(btn.dataset.challengeId);
      if (!Number.isFinite(id) || id === currentChallenge?.id) return;

      renderChallenge({ id, title: "Loading…", description: "" });
      renderCode({ snippets: { [selectedLang]: "" } }, selectedLang);
      if (reveal) {
        const list = document.getElementById("answers-list");
        if (list) list.innerHTML = "";
        const codeEl = document.getElementById("code-block");
        if (codeEl) wrapCodeLines(codeEl);
      }

      try {
        const next = await fetchChallenge(id);
        currentChallenge = next;
        setStored("cr_challenge", String(id));
        setActiveChallengeButton(id);
        renderChallenge(currentChallenge);
        renderCode(currentChallenge, selectedLang);

        if (reveal) {
          const codeEl = document.getElementById("code-block");
          if (codeEl) wrapCodeLines(codeEl);
          currentAnswers = await fetchAnswers(id);
          const issues = currentAnswers?.languages?.[selectedLang] ?? [];
          if (codeEl) applyLineHighlights(codeEl, issues);
          renderAnswersPanel(issues, selectedLang);
        }
      } catch {
        showToast("Could not load challenge.");
        setActiveChallengeButton(currentChallenge?.id);
        renderChallenge(currentChallenge);
        renderCode(currentChallenge, selectedLang);
        if (reveal) {
          const codeEl = document.getElementById("code-block");
          if (codeEl) wrapCodeLines(codeEl);
        }
      }
    });
  });

  const copyBtn = document.getElementById("copy-btn");
  copyBtn?.addEventListener("click", async () => {
    const snippet = currentChallenge?.snippets?.[selectedLang] ?? "";
    try {
      await navigator.clipboard.writeText(snippet);
      showToast("Copied.");
    } catch {
      showToast("Copy failed.");
    }
  });

  const preferredChallengeId = Number(getStored("cr_challenge", ""));
  if (Number.isFinite(preferredChallengeId) && preferredChallengeId !== initial?.id) {
    const exists = challenges.some((c) => c.id === preferredChallengeId);
    if (exists) {
      try {
        const next = await fetchChallenge(preferredChallengeId);
        currentChallenge = next;
        setActiveChallengeButton(preferredChallengeId);
        renderChallenge(currentChallenge);
        renderCode(currentChallenge, selectedLang);

        if (reveal) {
          const codeEl = document.getElementById("code-block");
          if (codeEl) wrapCodeLines(codeEl);
          currentAnswers = await fetchAnswers(preferredChallengeId);
          const issues = currentAnswers?.languages?.[selectedLang] ?? [];
          if (codeEl) applyLineHighlights(codeEl, issues);
          renderAnswersPanel(issues, selectedLang);
        }
      } catch {
        // ignore
      }
    }
  }
});

