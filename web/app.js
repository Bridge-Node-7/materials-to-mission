"use strict";

const DATA_URL = "./data/ga001.json";

const escapeHtml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const formatDate = (value) => {
  if (!value) return "Undated";
  const date = new Date(`${value}T00:00:00Z`);
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(date);
};

const actionCopy = {
  monitor: "Keep the evidence state visible and schedule a bounded reassessment when material conditions change.",
  validate: "Target the highest-consequence unknown with a defined proof request before advancing the pathway.",
  support: "Direct bounded support toward evidence or capability that closes a named pathway gap without implying qualification.",
  accelerate: "Increase tempo only after prerequisites and authorities are explicitly demonstrated.",
  surge: "Reserve exceptional effort for a human-owned, evidence-supported need with explicit consequence and authority.",
};

function renderTrace(nodes) {
  const list = document.querySelector("#trace-list");
  list.innerHTML = nodes
    .map(
      (node, index) => `
        <li class="trace-node" data-state="${escapeHtml(node.state)}">
          <div class="trace-dot" aria-hidden="true">${String(index + 1).padStart(2, "0")}</div>
          <h3>${escapeHtml(node.kind.replaceAll("-", " "))}</h3>
          <p>${escapeHtml(node.label)}</p>
          <span class="state-text">${escapeHtml(node.state)}</span>
        </li>`
    )
    .join("");
}

function renderSupport(items, sources, claims) {
  const sourceById = Object.fromEntries(sources.map((source) => [source.source_id, source]));
  const claimById = Object.fromEntries(claims.map((claim) => [claim.claim_id, claim]));
  const root = document.querySelector("#support-list");
  root.innerHTML = items
    .map((item) => {
      const claim = claimById[item.id];
      const matched =
        claim && claim.source_ids && claim.source_ids.length
          ? sourceById[claim.source_ids[0]]
          : null;

      return `
        <details class="support-item">
          <summary>
            <div class="support-summary">
              <div>
                <span class="support-id">${escapeHtml(item.id)}</span>
                <strong>${escapeHtml(item.claim)}</strong>
              </div>
              <span class="status ${escapeHtml(item.support_state)}">${escapeHtml(item.support_state)}</span>
            </div>
          </summary>
          <div class="support-body">
            <p>This displayed claim is a controlled public-view paraphrase. Open the official publisher source for the underlying public record.</p>
            <dl>
              <div>
                <dt>Source label</dt>
                <dd>${escapeHtml(item.source_label)}</dd>
              </div>
              <div>
                <dt>Source date</dt>
                <dd>${escapeHtml(formatDate(item.source_date))}</dd>
              </div>
              <div>
                <dt>Validation profile</dt>
                <dd id="support-profile-${escapeHtml(item.id)}">m0-strict-0.2.0</dd>
              </div>
              ${
                matched
                  ? `<div><dt>Official source</dt><dd><a href="${escapeHtml(matched.url)}" target="_blank" rel="noreferrer">${escapeHtml(matched.publisher)} ↗</a></dd></div>`
                  : ""
              }
            </dl>
          </div>
        </details>`;
    })
    .join("");
}

function renderInterpretations(items) {
  const supported = document.querySelector("#supported-interpretations");
  const unknown = document.querySelector("#unknown-interpretations");

  supported.innerHTML = items
    .filter((item) => item.state === "supported")
    .map((item) => `<li>${escapeHtml(item.text)}</li>`)
    .join("");

  unknown.innerHTML = items
    .filter((item) => item.state === "unknown")
    .map((item) => `<li>${escapeHtml(item.text)}</li>`)
    .join("");
}

function renderActions(actions) {
  const root = document.querySelector("#action-options");
  root.innerHTML = actions
    .map(
      (action, index) => `
        <article class="action-card">
          <span class="action-number">${String(index + 1).padStart(2, "0")}</span>
          <h3>${escapeHtml(action[0].toUpperCase() + action.slice(1))}</h3>
          <p>${escapeHtml(actionCopy[action] || "Human review required before any consequential action.")}</p>
          <small>Evidence-supported option · human decision required</small>
        </article>`
    )
    .join("");
}

function renderSources(sources) {
  const root = document.querySelector("#source-register");
  root.innerHTML = sources
    .map(
      (source) => `
        <article class="source-card">
          <div class="source-id">${escapeHtml(source.source_id)}</div>
          <div>
            <h3>${escapeHtml(source.title)}</h3>
            <p>${escapeHtml(source.publisher)} · ${escapeHtml(formatDate(source.source_date))}</p>
          </div>
          <a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">Official source ↗</a>
        </article>`
    )
    .join("");
}

function bindAuthorityDialog() {
  const dialog = document.querySelector("#authority-dialog");
  document.querySelectorAll("[data-open-authority]").forEach((button) => {
    button.addEventListener("click", () => dialog.showModal());
  });
}

async function init() {
  const response = await fetch(DATA_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Evidence view failed to load: HTTP ${response.status}`);
  }

  const data = await response.json();
  const { view, snapshot, sources } = data;

  document.querySelector("#arrival-scope").textContent = snapshot.evidence_scope;
  document.querySelector("#gallium-scope").textContent = snapshot.evidence_scope;
  document.querySelector("#review-date").textContent = formatDate(snapshot.review_date);
  document.querySelector("#source-count").textContent = String(sources.sources.length);
  document.querySelector("#focus-sources").textContent = `${sources.sources.length} official sources`;
  document.querySelector("#profile").textContent = view.validation_profile;
  document.querySelector("#view-contract").textContent = view.view_contract_version;
  document.querySelector("#toolkit").textContent = view.toolkit_version;

  renderTrace(view.trace_nodes);
  renderSupport(view.support_items, sources.sources, snapshot.claims);
  renderInterpretations(snapshot.bounded_interpretations);
  renderActions(view.action_options);
  renderSources(sources.sources);
  bindAuthorityDialog();
}

init().catch((error) => {
  const main = document.querySelector("#main");
  main.innerHTML = `
    <section class="section examine-field">
      <div class="evidence-panel boundary">
        <span class="status unknown">Evidence unavailable</span>
        <h1>Public evidence view could not be loaded.</h1>
        <p>${escapeHtml(error.message)}</p>
        <p>No favorable status has been inferred from missing data.</p>
      </div>
    </section>`;
  console.error(error);
});
