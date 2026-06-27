const REFRESH_MS = 2000;

const els = {
  status: document.querySelector("#status"),
  source: document.querySelector("#source"),
  character: document.querySelector("#character"),
  actFloor: document.querySelector("#act-floor"),
  hp: document.querySelector("#hp"),
  gold: document.querySelector("#gold"),
  boss: document.querySelector("#boss"),
  elite: document.querySelector("#elite"),
  risk: document.querySelector("#risk"),
  riskBar: document.querySelector("#risk-bar"),
  needs: document.querySelector("#needs"),
  strengths: document.querySelector("#strengths"),
  warnings: document.querySelector("#warnings"),
  updated: document.querySelector("#updated"),
  decisions: document.querySelector("#decisions"),
};

async function refresh() {
  try {
    const response = await fetch("/api/state", { cache: "no-store" });
    const payload = await response.json();
    if (!payload.ok) {
      renderError(payload);
      return;
    }
    render(payload);
  } catch (error) {
    renderError({ error: error.message || String(error) });
  }
}

function render(payload) {
  els.status.textContent = "Live";
  els.status.className = "status-pill ok";
  els.source.textContent = basename(payload.source);
  els.updated.textContent = new Date().toLocaleTimeString();

  const state = payload.state;
  els.character.textContent = state.character;
  els.actFloor.textContent = `${state.act} / F${state.floor}`;
  els.hp.textContent = `${state.hp}/${state.max_hp}`;
  els.gold.textContent = state.gold;
  els.boss.textContent = state.boss || "-";
  els.elite.textContent = state.next_elite || "-";

  const profile = payload.profile;
  els.risk.textContent = `Risk ${Math.round(profile.risk)}`;
  els.riskBar.style.width = `${Math.min(100, profile.risk)}%`;
  renderChips(els.needs, profile.needs, "No urgent gaps");
  renderChips(els.strengths, profile.strengths.slice(0, 18), "No tagged strengths yet");
  renderWarnings(profile.warnings);
  renderDecisions(payload.decisions);
}

function renderError(payload) {
  els.status.textContent = "Check JSON";
  els.status.className = "status-pill error";
  els.decisions.innerHTML = `<div class="error-box">${escapeHtml(payload.error || "Unknown error")}</div>`;
  els.updated.textContent = new Date().toLocaleTimeString();
}

function renderChips(target, items, emptyText) {
  if (!items || items.length === 0) {
    target.innerHTML = `<span class="chip">${escapeHtml(emptyText)}</span>`;
    return;
  }
  target.innerHTML = items.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("");
}

function renderWarnings(items) {
  if (!items || items.length === 0) {
    els.warnings.innerHTML = "<li>No major warnings</li>";
    return;
  }
  els.warnings.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderDecisions(decisions) {
  if (!decisions || decisions.length === 0) {
    els.decisions.innerHTML = `<div class="empty">JSON loaded. Add decisions to the state file to get recommendations.</div>`;
    return;
  }
  els.decisions.innerHTML = decisions.map(renderDecision).join("");
}

function renderDecision(decision) {
  return `
    <article class="decision-card">
      <div class="decision-top">
        <div class="topic">${escapeHtml(decision.topic)}</div>
        <div class="summary">${escapeHtml(decision.summary)}</div>
      </div>
      ${decision.recommendations.map(renderRecommendation).join("")}
    </article>
  `;
}

function renderRecommendation(item) {
  const reasons = item.reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("");
  const cautions = item.cautions.map((caution) => `<li>${escapeHtml(caution)}</li>`).join("");
  return `
    <section class="recommendation">
      <div class="score">${escapeHtml(String(item.score))}</div>
      <div class="rec-body">
        <h3>${escapeHtml(item.choice)}</h3>
        <ul class="reason-list">${reasons}</ul>
        ${cautions ? `<ul class="caution-list">${cautions}</ul>` : ""}
      </div>
    </section>
  `;
}

function basename(path) {
  if (!path) return "-";
  return path.split(/[\\/]/).pop();
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

refresh();
setInterval(refresh, REFRESH_MS);
