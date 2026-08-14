"use strict";
(() => {
  const node = document.getElementById("publicData");
  if (!node) return;

  const payload = JSON.parse(node.textContent);
  const atlas = payload.atlas;
  const forms = payload.forms;
  const sources = payload.sources;
  const yigPathway = payload.yig001;
  const ga001 = payload.ga001;
  const materials = atlas.materials;
  const byId = Object.fromEntries(materials.map(item => [item.id, item]));
  const byName = Object.fromEntries(materials.map(item => [item.name, item]));
  const formById = Object.fromEntries(forms.map(item => [item.id, item]));
  const sourceById = Object.fromEntries(sources.map(item => [item.source_id, item]));
  const lensMap = atlas.lenses;

  const nodes = [...document.querySelectorAll(".mineral")];
  const lensButtons = [...document.querySelectorAll(".lens")];
  const detail = document.getElementById("desktopDetail");
  const sheet = document.getElementById("materialSheet");
  const sheetContent = document.getElementById("sheetContent");
  const search = document.getElementById("globalSearch");
  const results = document.getElementById("searchResults");
  const field = document.getElementById("field");
  const fieldViewport = document.querySelector(".field-viewport");
  const svg = document.getElementById("connectionLayer");
  const lensCount = document.getElementById("lensCount");
  const constellation = document.getElementById("constellationPanel");
  const index = document.getElementById("indexPanel");
  const constellationBtn = document.getElementById("constellationView");
  const indexBtn = document.getElementById("indexView");
  const experienceStatus = document.getElementById("experienceStatus");
  const workspace = document.getElementById("constellationPanel");
  const depthSections = [...document.querySelectorAll(".contextual-depth")];
  let activeLens = "all";
  let selectedId = null;
  let activeResult = -1;
  const preferredScrollBehavior = () =>
    matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";

  function announce(message) {
    if (!experienceStatus) return;
    experienceStatus.textContent = message;
  }

  function clearActiveDescendant() {
    search.removeAttribute("aria-activedescendant");
    activeResult = -1;
  }
  function setDepthState(state, {scrollId=null}={}) {
    const visible = {
      arrival: [], explore: [], trace: ["gallium", "trace"],
      "trace-next": ["gallium", "trace", "decision"],
      proof: ["gallium", "trace", "examine", "decision", "sources"],
      forms: ["forms"], yig: ["forms", "yig-pathway", "sources"], sources: ["sources"]
    }[state] || [];
    depthSections.forEach(section => section.classList.toggle("is-revealed", visible.includes(section.id)));
    document.body.dataset.depth = state;
    if (scrollId) requestAnimationFrame(() => document.getElementById(scrollId)?.scrollIntoView({block:"start", behavior:preferredScrollBehavior()}));
  }
  function clearSelection({announceState=false}={}) {
    selectedId = null;
    field.classList.remove("form-mode");
    nodes.forEach((node,index) => {
      node.classList.remove("selected", "related-parent", "selected-exception");
      node.removeAttribute("aria-current");
      node.tabIndex = index === 0 ? 0 : -1;
    });
    svg.replaceChildren(); workspace.classList.remove("has-selection");
    detail.innerHTML = '<div class="neutral-detail"><p class="eyebrow">EXPLORE</p><h2>Choose a material</h2><p>Explore its applications, related material systems, public sources, and reviewed pathways where available.</p></div>';
    setDepthState("arrival"); if (sheet.open) sheet.close();
    if (announceState) announce("Materials-to-Mission Atlas. No material selected.");
  }
const esc = value => String(value).replace(/[&<>"']/g, char => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  })[char]);

  const linkedForms = name => forms.filter(form =>
    form.relationships.some(rel => rel.mineral === name)
  );

  const lensChips = material => material.lenses.length
    ? material.lenses.map(id => `<span>${esc(lensMap[id].short)}</span>`).join("")
    : `<span>No DOE application row mapped in this controlled snapshot.</span>`;

  const sourceLinks = material => material.source_ids
    .map(id => sourceById[id])
    .filter(Boolean)
    .map(source => `<a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">${esc(source.source_id)} ↗</a>`)
    .join("");

  // V070:DISCOVERABLE_DEPTH
  function depthDrawer(layer, title, status, body, tone="baseline") {
    return `<details class="depth-drawer" data-layer="${esc(layer)}">
      <summary>
        <span class="depth-name">${esc(title)}</span>
        <small class="depth-status depth-${esc(tone)}">${esc(status)}</small>
        <span class="depth-chevron" aria-hidden="true">⌄</span>
      </summary>
      <div class="depth-drawer-body">${body}</div>
    </details>`;
  }
  function depthRail(kind, drawers) {
    return `<div class="depth-rail" data-depth-rail="${esc(kind)}">
      <div class="depth-rail-head">
        <span>MORE TO EXPLORE</span>
        <small>4 deeper layers</small>
      </div>
      ${drawers.join("")}
    </div>`;
  }
  function materialDetail(material, sheetMode=false) {
    const related = linkedForms(material.name);
    const contexts = (material.context || []).map(context =>
      `<span><b>${esc(context.label)}</b><br>${esc(context.detail)}</span>`
    ).join("");
    const titleId = sheetMode ? ' id="sheetTitle"' : "";
    const formHtml = related.length
      ? related.map(form =>
          `<button type="button" class="form-chip" data-form-id="${esc(form.id)}">${esc(form.symbol)} · ${esc(form.name)}</button>`
        ).join("")
      : `<span>No public material system linked in this release.</span>`;

    const reviewed = material.review?.code === "reviewed-pathway";
    const pathwayBody = reviewed
      ? `<p class="depth-copy">A reviewed public-source pathway is available for this material.</p>
         <a class="detail-action" data-depth="trace" href="#trace">Reviewed pathway available →</a>
         <small class="review-boundary">Public-source review · not qualification</small>`
      : `<p class="depth-copy"><strong>Baseline context.</strong> No reviewed end-to-end pathway has been released for this material. Available public context remains visible in the other layers.</p>`;

    const connectionBody = `<span class="depth-body-label">Applications</span><div class="chips">${lensChips(material)}</div>
      ${contexts ? `<div class="depth-context"><span class="depth-body-label">Public context</span><div class="context-list">${contexts}</div></div>` : ""}`;
    const systemBody = `<div class="chips">${formHtml}</div>`;
    const evidenceBody = `<div class="depth-evidence-state">
        <span class="depth-body-label">Evidence review</span>
        <strong class="review-state review-${esc(material.review.code)}">${esc(material.review.label)}</strong>
      </div>
      <div class="depth-context"><span class="depth-body-label">Sources & provenance</span><div class="source-links">${sourceLinks(material)}</div></div>`;

    const connectionStatus = material.lenses.length ? `${material.lenses.length} ${material.lenses.length === 1 ? "CONNECTION" : "CONNECTIONS"}` : "BASELINE";
    const systemStatus = related.length ? `${related.length} ${related.length === 1 ? "SYSTEM" : "SYSTEMS"}` : "NONE RELEASED";
    const sourceStatus = `${material.source_ids.length} ${material.source_ids.length === 1 ? "SOURCE" : "SOURCES"}`;

    const rail = depthRail("material", [
      depthDrawer("connections", "Connections", connectionStatus, connectionBody),
      depthDrawer("systems", "Material systems", systemStatus, systemBody),
      depthDrawer("evidence", "Evidence basis", sourceStatus, evidenceBody),
      depthDrawer("pathway", "Pathway & proof", reviewed ? "REVIEWED" : "BASELINE", pathwayBody, reviewed ? "reviewed" : "baseline"),
    ]);

    return `<div class="material-detail">
      <div class="detail-title">
        <span class="big-symbol">${esc(material.symbol)}</span>
        <div><p class="eyebrow">${material.rare_earth ? "RARE EARTH · " : ""}USGS 2025</p>
        <h2${titleId}>${esc(material.name)}</h2><p>${esc(material.official_designation)}</p></div>
      </div>
      ${rail}
    </div>`;
  }
  function formDetail(form, sheetMode=false) {
    const relationships = form.relationships.map(rel => {
      const material = byName[rel.mineral];
      return material
        ? `<button type="button" class="form-chip parent-link" data-parent-id="${esc(material.id)}">${esc(material.name)} · ${esc(rel.relation.replaceAll("-"," "))}</button>`
        : "";
    }).join("");
    const src = form.source_ids
      .map(id => sourceById[id])
      .filter(Boolean)
      .map(source => `<a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">${esc(source.source_id)} ↗</a>`)
      .join("");
    const titleId = sheetMode ? ' id="sheetTitle"' : "";
    const review = form.review?.label || "Public Context";
    const displayFormula = form.id === "yig" ? "Y₃Fe₅O₁₂" : form.formula;
    const formula = displayFormula ? ` · ${esc(displayFormula)}` : "";
    const hasPathway = Boolean(form.pathway_id);
    const action = hasPathway
      ? `<a class="detail-action" data-depth="${esc(form.pathway_id === "YIG-001" ? "yig" : "forms")}" href="${form.pathway_id === "YIG-001" ? "#yig-pathway" : "#forms"}">Reviewed context available →</a>`
      : "";
    const pathwayBody = hasPathway
      ? `<p class="depth-copy">Reviewed public context extends beyond the baseline for this engineered system.</p>${action}`
      : `<p class="depth-copy"><strong>Baseline context.</strong> No deeper reviewed pathway has been released for this engineered system.</p>`;

    const rail = depthRail("form", [
      depthDrawer("connections", "Connections", `${form.relationships.length} ${form.relationships.length === 1 ? "MINERAL" : "MINERALS"}`, `<div class="chips">${relationships || "<span>No public critical-mineral relationship released.</span>"}</div>`),
      depthDrawer("context", "System context", displayFormula ? "FORMULA + CONTEXT" : "PUBLIC CONTEXT", `<p class="depth-copy">${esc(form.context)}${formula}</p>`),
      depthDrawer("evidence", "Evidence basis", `${form.source_ids.length} ${form.source_ids.length === 1 ? "SOURCE" : "SOURCES"}`, `<div class="depth-evidence-state"><span class="depth-body-label">Evidence review</span><strong class="review-state">${esc(review)}</strong></div><div class="depth-context"><span class="depth-body-label">Source basis</span><div class="source-links">${src}</div></div>`),
      depthDrawer("pathway", "Pathway & proof", hasPathway ? "REVIEWED CONTEXT" : "BASELINE", pathwayBody, hasPathway ? "reviewed" : "baseline"),
    ]);

    return `<div class="material-detail">
      <div class="detail-title"><span class="big-symbol">${esc(form.symbol)}</span>
      <div><p class="eyebrow">ENGINEERED MATERIAL / SYSTEM</p><h2${titleId}>${esc(form.name)}</h2><p>${esc(form.context)}${formula}</p></div></div>
      ${rail}
    </div>`;
  }

  function bindDetail(root) {
    root.querySelectorAll("[data-form-id]").forEach(button =>
      button.addEventListener("click", () => selectForm(button.dataset.formId, {pushHash:true, openSheet:true}))
    );
    root.querySelectorAll(".parent-link").forEach(button =>
      button.addEventListener("click", () => selectMaterial(button.dataset.parentId, {pushHash:true, openSheet:true}))
    );
    root.querySelectorAll("[data-depth]").forEach(link => link.addEventListener("click", event => {
      event.preventDefault(); const target = link.dataset.depth;
      if (target === "trace") { setDepthState("trace", {scrollId:"trace"}); setHash("#trace", true); }
      else if (target === "yig") { setDepthState("yig", {scrollId:"yig-pathway"}); setHash("#yig-pathway", true); }
      else if (target === "forms") { setDepthState("forms", {scrollId:"forms"}); setHash("#forms", true); }
    }));
  }

  function updateNodeState(id) {
    selectedId = id; workspace.classList.toggle("has-selection", Boolean(id));
    nodes.forEach((node,index) => {
      const on = Boolean(id) && node.dataset.id === id;
      node.classList.toggle("selected", on);
      if (on) node.setAttribute("aria-current", "true"); else node.removeAttribute("aria-current");
      node.tabIndex = on ? 0 : (!id && index === 0 ? 0 : -1);
    });
  }

  function directionalNeighbor(current, key) {
    const box = current.getBoundingClientRect();
    const cx = box.left + box.width/2;
    const cy = box.top + box.height/2;
    const candidates = nodes.filter(node => node !== current && !node.classList.contains("dim")).map(node => {
      const rect = node.getBoundingClientRect();
      const x = rect.left + rect.width/2;
      const y = rect.top + rect.height/2;
      const dx = x - cx, dy = y - cy;
      const inDirection =
        (key === "ArrowRight" && dx > 3) ||
        (key === "ArrowLeft" && dx < -3) ||
        (key === "ArrowDown" && dy > 3) ||
        (key === "ArrowUp" && dy < -3);
      if (!inDirection) return null;
      const primary = (key === "ArrowRight" || key === "ArrowLeft") ? Math.abs(dx) : Math.abs(dy);
      const cross = (key === "ArrowRight" || key === "ArrowLeft") ? Math.abs(dy) : Math.abs(dx);
      return {node, score: primary + cross * 1.8};
    }).filter(Boolean).sort((a,b) => a.score - b.score);
    return candidates[0]?.node || null;
  }

  function enableConstellationKeyboard() {
    nodes.forEach((node,index) => {
      node.tabIndex = selectedId ? (node.dataset.id === selectedId ? 0 : -1) : (index === 0 ? 0 : -1);
      node.addEventListener("keydown", event => {
        if (!["ArrowRight","ArrowLeft","ArrowDown","ArrowUp"].includes(event.key)) return;
        event.preventDefault();
        const next = directionalNeighbor(node, event.key);
        if (!next) return;
        selectMaterial(next.dataset.id, {pushHash:true, openSheet:false});
        next.focus();
      });
    });
  }

  function centerMaterialInViewport(id) {
    if (!fieldViewport || !matchMedia("(max-width:900px)").matches) return;
    const node = document.querySelector(`.mineral[data-id="${CSS.escape(id)}"]`);
    if (!node) return;
    const target = Math.max(0, node.offsetLeft - fieldViewport.clientWidth / 2);
    fieldViewport.scrollTo({left: target, behavior:"auto"});
  }

  function setHash(value, push=true) {
    if (location.hash === value) return;
    if (push) history.pushState(null, "", value);
    else history.replaceState(null, "", value);
  }

  function selectMaterial(id, options={}) {
    const {pushHash=false, openSheet=true} = options;
    const material = byId[id];
    if (!material) return;
    field.classList.remove("form-mode");
    nodes.forEach(node => node.classList.remove("related-parent"));
    updateNodeState(id);
    setDepthState("explore");
    detail.innerHTML = materialDetail(material, false);
    bindDetail(detail);
    drawConnections(material);
    requestAnimationFrame(() => centerMaterialInViewport(material.id));
    if (openSheet && matchMedia("(max-width:1160px)").matches) {
      sheetContent.innerHTML = materialDetail(material, true);
      bindDetail(sheetContent);
      if (!sheet.open) sheet.show();
    }
    announce(`${material.name}. ${material.review.label}.`);
    if (pushHash) setHash(`#material-${material.id}`, true);
  }

  function selectForm(id, options={}) {
    const {pushHash=false, openSheet=true} = options;
    const form = formById[id];
    if (!form) return;
    const parentIds = form.relationships.map(rel => byName[rel.mineral]?.id).filter(Boolean);
    field.classList.add("form-mode");
    setDepthState("explore");
    workspace.classList.add("has-selection");
    nodes.forEach(node => node.classList.toggle("related-parent", parentIds.includes(node.dataset.id)));
    if (parentIds.length) updateNodeState(parentIds[0]);
    if (matchMedia("(min-width:1161px)").matches) {
      detail.innerHTML = formDetail(form, false);
      bindDetail(detail);
    } else if (openSheet) {
      sheetContent.innerHTML = formDetail(form, true);
      bindDetail(sheetContent);
      if (!sheet.open) sheet.show();
    }
    announce(`${form.name}. ${form.review?.label || "Public context"}.`);
    if (pushHash) setHash(`#form-${form.id}`, true);
  }

  function restoreFromHash({initial=false}={}) {
    const hash = location.hash;
    if (!hash.startsWith("#material-") && !hash.startsWith("#form-") && sheet.open) sheet.close();
    if (hash === "#indexPanel") setAtlasView("index", {focus:false, scroll:false}); else setAtlasView("constellation", {focus:false, scroll:false});
    if (hash.startsWith("#material-")) { const id=hash.slice(10); if (byId[id]) { selectMaterial(id,{pushHash:false,openSheet:true}); return; } }
    if (hash.startsWith("#form-")) { const id=hash.slice(6); if (formById[id]) { selectForm(id,{pushHash:false,openSheet:true}); return; } }
    if (hash === "#gallium") { selectMaterial("gallium",{pushHash:false,openSheet:true}); return; }
    if (["#trace","#examine","#decision"].includes(hash)) { selectMaterial("gallium",{pushHash:false,openSheet:false}); const state=hash==="#trace"?"trace":(hash==="#decision"?"trace-next":"proof"); setDepthState(state,{scrollId:hash.slice(1)}); return; }
    if (hash === "#yig-pathway") { selectForm("yig",{pushHash:false,openSheet:false}); setDepthState("yig",{scrollId:"yig-pathway"}); return; }
    if (hash === "#forms") { clearSelection(); setDepthState("forms",{scrollId:"forms"}); return; }
    if (hash === "#sources") { clearSelection(); setDepthState("sources",{scrollId:"sources"}); return; }
    if (hash.startsWith("#ga-source-")) { selectMaterial("gallium",{pushHash:false,openSheet:false}); setDepthState("proof",{scrollId:hash.slice(1)}); return; }
    if (!hash || hash === "#atlas" || initial) { clearSelection({announceState:initial}); return; }
    clearSelection();
  }

  function applyLens() {
    const active = activeLens === "all" ? null : lensMap[activeLens];
    let count = 0;
    nodes.forEach(node => {
      const material = byId[node.dataset.id];
      const hit = !active || material.lenses.includes(activeLens);
      if (hit) count += 1;
      const selectedException = Boolean(active) && !hit && node.dataset.id === selectedId;
      node.classList.toggle("dim", Boolean(active) && !hit && !selectedException);
      node.classList.toggle("selected-exception", selectedException);
      node.classList.toggle("lens-hit", Boolean(active) && hit);
      if (active) node.style.setProperty("--active-lens", active.color);
      else node.style.removeProperty("--active-lens");
    });
    lensCount.textContent = active ? `${count} of 60 · ${active.label}` : "60 minerals · USGS 2025";
    field.classList.toggle("lens-filtered", Boolean(active));
    if (selectedId && active && !byId[selectedId].lenses.includes(activeLens)) announce(`${byId[selectedId].name}. Selected, outside current filter.`);
    drawConnections(selectedId ? byId[selectedId] : null);
  }

  lensButtons.forEach(button => button.addEventListener("click", () => {
    activeLens = button.dataset.lens;
    lensButtons.forEach(item => {
      const on = item === button;
      item.classList.toggle("active", on);
      item.setAttribute("aria-pressed", String(on));
    });
    applyLens();
  }));

  function drawConnections(material) {
    svg.replaceChildren();
    if (!material) return;
    const node = document.querySelector(`.mineral[data-id="${CSS.escape(material.id)}"]`);
    if (!node) return;
    const fieldRect = field.getBoundingClientRect();
    const nodeRect = node.getBoundingClientRect();
    const x1 = nodeRect.left + nodeRect.width/2 - fieldRect.left;
    const y1 = nodeRect.top + nodeRect.height/2 - fieldRect.top;
    const ids = activeLens !== "all" && material.lenses.includes(activeLens)
      ? [activeLens] : material.lenses;

    ids.forEach(id => {
      const zone = field.querySelector(`[data-zone="${CSS.escape(id)}"]`);
      if (!zone) return;
      const rect = zone.getBoundingClientRect();
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", x1);
      line.setAttribute("y1", y1);
      line.setAttribute("x2", rect.left + rect.width/2 - fieldRect.left);
      line.setAttribute("y2", rect.top + rect.height/2 - fieldRect.top);
      line.setAttribute("class", "connection-line");
      line.style.stroke = lensMap[id].color;
      line.style.color = lensMap[id].color;
      svg.appendChild(line);
    });
  }

  nodes.forEach(node => node.addEventListener("click", event => {
    event.preventDefault();
    selectMaterial(node.dataset.id, {pushHash:true, openSheet:true});
  }));

  const entityKindLabel = item => {
    if (item.type === "mineral") return "USGS 2025 Critical Mineral";
    const labels = {
      "engineered-material-system":"Engineered Material System",
      "engineered-substrate":"Engineered Substrate",
      "engineered-material":"Engineered Material",
      "engineered-critical-material":"Engineered Critical Material",
      "magnet-family":"Magnet Material Family",
      "semiconductor":"Engineered Semiconductor",
      "compound-semiconductor":"Compound Semiconductor"
    };
    return labels[item.kind] || "Engineered Material / System";
  };

  const entityShortLabel = item => {
    if (item.type === "mineral") return "Mineral";
    const labels = {
      "engineered-material-system":"Material System",
      "engineered-substrate":"Substrate",
      "engineered-material":"Material",
      "engineered-critical-material":"Critical Material",
      "magnet-family":"Magnet Family",
      "semiconductor":"Semiconductor",
      "compound-semiconductor":"Semiconductor"
    };
    return labels[item.kind] || "Material System";
  };

  const score = (item, query) => {
    const symbol = item.symbol.toLowerCase();
    const name = item.name.toLowerCase();
    if (symbol === query) return 0;
    if (name === query) return 1;
    if (symbol.startsWith(query)) return 2;
    if (name.startsWith(query)) return 3;
    if (symbol.includes(query)) return 4;
    if (name.includes(query)) return 5;
    return 99;
  };

  function searchItems() {
    const query = search.value.trim().toLowerCase();
    clearActiveDescendant();
    if (!query) { results.hidden = true; search.setAttribute("aria-expanded", "false"); return; }
    const items = [...materials.map(item => ({...item, type:"mineral"})), ...forms.map(item => ({...item, type:"form"}))]
      .map(item => ({item, score:score(item, query)})).filter(entry => entry.score < 99)
      .sort((a,b) => a.score - b.score || a.item.name.localeCompare(b.item.name)).slice(0,12).map(entry => entry.item);
    const renderSearchResult = item => {
      const button = document.createElement("button"); button.type="button"; button.className="search-result";
      button.setAttribute("role","option"); button.setAttribute("aria-selected","false");
      button.id = `search-option-${item.type}-${item.id}`; button.dataset.resultType=item.type; button.dataset.resultId=item.id;
      const symbol=document.createElement("span"); symbol.className="r-symbol"; symbol.textContent=item.symbol;
      const label=document.createElement("span"); const name=document.createElement("strong"); name.textContent=item.name;
      const kind=document.createElement("small"); kind.textContent=entityKindLabel(item); label.append(name,kind);
      const short=document.createElement("span"); short.textContent=entityShortLabel(item); button.append(symbol,label,short); return button;
    };
    const renderNoResult = () => {
      const row=document.createElement("div"); row.className="search-result"; const symbol=document.createElement("span"); symbol.className="r-symbol"; symbol.textContent="0";
      const label=document.createElement("span"); const name=document.createElement("strong"); name.textContent="No public result";
      const hint=document.createElement("small"); hint.textContent="Try another official mineral or material system."; label.append(name,hint); row.append(symbol,label,document.createElement("span")); return row;
    };
    results.replaceChildren(...(items.length ? items.map(renderSearchResult) : [renderNoResult()]));
    results.hidden=false; search.setAttribute("aria-expanded","true");
    announce(items.length ? `${items.length} results available.` : "No public result.");
    results.querySelectorAll("button").forEach(button => button.addEventListener("click", () => activateResult(button)));
  }

  function activateResult(button) {
    results.hidden=true; search.setAttribute("aria-expanded","false"); clearActiveDescendant(); search.value=""; activeLens="all";
    lensButtons.forEach(item => { const on=item.dataset.lens === "all"; item.classList.toggle("active",on); item.setAttribute("aria-pressed",String(on)); });
    applyLens();
    if (button.dataset.resultType === "mineral") selectMaterial(button.dataset.resultId,{pushHash:true,openSheet:true});
    else selectForm(button.dataset.resultId,{pushHash:true,openSheet:true});
  }

  function moveResult(delta) {
    const options=[...results.querySelectorAll("button[role=option]")]; if (!options.length) return;
    activeResult=(activeResult+delta+options.length)%options.length;
    options.forEach((option,index)=>option.setAttribute("aria-selected",String(index===activeResult)));
    options[activeResult].scrollIntoView({block:"nearest"}); search.setAttribute("aria-activedescendant",options[activeResult].id);
  }

  search.addEventListener("input", searchItems);
  search.addEventListener("keydown", event => {
    if (event.key === "ArrowDown") {
      event.preventDefault(); moveResult(1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault(); moveResult(-1);
    } else if (event.key === "Enter" && activeResult >= 0) {
      event.preventDefault();
      const option = results.querySelectorAll("button[role=option]")[activeResult];
      if (option) activateResult(option);
    } else if (event.key === "Escape") {
      results.hidden = true;
      search.setAttribute("aria-expanded", "false");
      clearActiveDescendant();
    }
  });

  document.querySelectorAll(".form-card [data-form-id]").forEach(button =>
    button.addEventListener("click", event => {
      event.preventDefault();
      selectForm(button.dataset.formId, {pushHash:true, openSheet:true});
    })
  );
  const showNextProof = document.getElementById("showNextProof");
  if (showNextProof) showNextProof.addEventListener("click", () => { setDepthState("trace-next", {scrollId:"decision"}); setHash("#decision", true); });
  const showProof = document.getElementById("showProof");
  if (showProof) showProof.addEventListener("click", () => { setDepthState("proof", {scrollId:"examine"}); setHash("#examine", true); });

  document.getElementById("sheetClose").addEventListener("click", () => sheet.close());
  sheet.addEventListener("click", event => {
    if (event.target === sheet) sheet.close();
  });

  function setAtlasView(mode, {focus=false, scroll=false}={}) {
    const showIndex = mode === "index";
    constellation.hidden = showIndex;
    index.classList.toggle("is-active", showIndex);
    constellationBtn.setAttribute("aria-pressed", String(!showIndex));
    indexBtn.setAttribute("aria-pressed", String(showIndex));
    if (showIndex && scroll) index.scrollIntoView({block:"start",behavior:preferredScrollBehavior()});
    announce(showIndex ? "List view." : "Materials-to-Mission Atlas map view.");
    if (showIndex && focus) {
      const title = document.getElementById("index-title");
      title.setAttribute("tabindex","-1");
      title.focus({preventScroll:true});
    }
  }

  constellationBtn.addEventListener("click", () => setAtlasView("constellation"));
  indexBtn.addEventListener("click", () => setAtlasView("index"));

  const openIndexCta = document.getElementById("openIndexCta");
  if (openIndexCta) {
    openIndexCta.addEventListener("click", event => {
      event.preventDefault();
      history.replaceState(null, "", "#indexPanel");
      setAtlasView("index", {focus:true, scroll:true});
    });
  }

  document.querySelectorAll(".index-row").forEach(row =>
    row.addEventListener("toggle", () => {
      if (row.open && byId[row.dataset.indexId]) {
        updateNodeState(row.dataset.indexId);
        detail.innerHTML = materialDetail(byId[row.dataset.indexId], false);
        bindDetail(detail);
      }
    })
  );

  addEventListener("hashchange", () => restoreFromHash({initial:false}));

  addEventListener("popstate", () => restoreFromHash({initial:false}));
  addEventListener("resize", () => requestAnimationFrame(() => drawConnections(byId[selectedId])));

  document.documentElement.classList.add("js-ready");
  clearSelection();
  bindDetail(detail);
  applyLens();
  restoreFromHash({initial:true});
  enableConstellationKeyboard();
})();

// V070:SELECTED_PATHWAYS
(() => {
  const text = (node) => (node?.textContent || "").replace(/\s+/g, " ").trim();

  function findLegacyOverview() {
    return document.querySelector('[data-depth="legacy-overview"]');
  }

  function commonParent(a, b) {
    if (!a || !b) return null;
    let node = a.parentElement;
    while (node && node !== document.body) {
      if (node.contains(b)) return node;
      node = node.parentElement;
    }
    return null;
  }

  function enhanceSelectedPathways() {
    const section = document.getElementById("selected-pathways");
    const legacy = findLegacyOverview();
    if (!section || !legacy) return;
    legacy.hidden = true;
    legacy.setAttribute("aria-hidden", "true");
    legacy.dataset.v070SupersededOverview = "true";

    const buttons = [...document.querySelectorAll("button")];
    const map = buttons.find((b) => text(b) === "Map");
    const list = buttons.find((b) => text(b) === "List");
    const switcher = commonParent(map, list);

    if (switcher && !document.querySelector(".atlas-pathway-signpost")) {
      const cue = document.createElement("a");
      cue.className = "atlas-pathway-signpost";
      cue.href = "#selected-pathways";
      const pathwayCount = section.querySelectorAll(".selected-pathway-row").length;
      cue.innerHTML = `${pathwayCount} deeper public examples available <span aria-hidden="true">↓</span>`;
      switcher.insertAdjacentElement("afterend", cue);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhanceSelectedPathways, { once: true });
  } else {
    enhanceSelectedPathways();
  }
})();
