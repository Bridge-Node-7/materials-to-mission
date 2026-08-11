"use strict";
(() => {
  const node = document.getElementById("publicData");
  if (!node) return;

  const payload = JSON.parse(node.textContent);
  const atlas = payload.atlas;
  const forms = payload.forms;
  const sources = payload.sources;
  const yigPathway = payload.yig001;
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

  let activeLens = "all";
  let selectedId = "gallium";
  let activeResult = -1;

  function announce(message) {
    if (!experienceStatus) return;
    experienceStatus.textContent = message;
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
    const action = material.id === "gallium"
      ? `<a class="detail-action" href="#trace">Follow reviewed pathway →</a>`
      : `<a class="detail-action" href="#sources">View source basis →</a>`;

    return `<div class="material-detail">
      <div class="detail-title">
        <span class="big-symbol">${esc(material.symbol)}</span>
        <div><p class="eyebrow">${material.rare_earth ? "RARE EARTH · " : ""}USGS 2025</p>
        <h2${titleId}>${esc(material.name)}</h2><p>${esc(material.official_designation)}</p></div>
      </div>
      <section><span class="detail-label">Where it is used</span><div class="chips">${lensChips(material)}</div></section>
      <section><span class="detail-label">Evidence review</span><strong class="review-state review-${esc(material.review.code)}">${esc(material.review.label)}</strong></section>
      ${contexts ? `<section><span class="detail-label">Policy context</span><div class="context-list">${contexts}</div></section>` : ""}
      <section><span class="detail-label">Related Material Systems</span><div class="chips">${formHtml}</div></section>
      <section><span class="detail-label">Sources & provenance</span><div class="source-links">${sourceLinks(material)}</div></section>
      ${action}
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
    const primary = form.primary_example ? `<span class="primary-badge">Primary example</span>` : "";
    const displayFormula = form.id === "yig" ? "Y₃Fe₅O₁₂" : form.formula;
    const formula = displayFormula ? ` · ${esc(displayFormula)}` : "";
    const action = form.pathway_id === "YIG-001"
      ? `<a class="detail-action" href="#yig-pathway">Trace YIG source-to-mission path →</a>`
      : `<a class="detail-action" href="#forms">Explore material systems →</a>`;
    return `<div class="material-detail">
      <div class="detail-title"><span class="big-symbol">${esc(form.symbol)}</span>
      <div>${primary}<p class="eyebrow">ENGINEERED MATERIAL / SYSTEM</p><h2${titleId}>${esc(form.name)}</h2><p>${esc(form.context)}${formula}</p></div></div>
      <section><span class="detail-label">Evidence review</span><strong class="review-state">${esc(review)}</strong></section>
      <section><span class="detail-label">Related critical minerals</span><div class="chips">${relationships}</div></section>
      <section><span class="detail-label">Source basis</span><div class="source-links">${src}</div></section>
      ${action}
    </div>`;
  }

  function bindDetail(root) {
    root.querySelectorAll("[data-form-id]").forEach(button =>
      button.addEventListener("click", () => selectForm(button.dataset.formId, {pushHash:true, openSheet:true}))
    );
    root.querySelectorAll(".parent-link").forEach(button =>
      button.addEventListener("click", () => selectMaterial(button.dataset.parentId, {pushHash:true, openSheet:true}))
    );
  }

  function updateNodeState(id) {
    selectedId = id;
    nodes.forEach(node => {
      const on = node.dataset.id === id;
      node.classList.toggle("selected", on);
      node.setAttribute("aria-current", on ? "true" : "false");
      node.tabIndex = on ? 0 : -1;
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
    nodes.forEach(node => {
      node.tabIndex = node.dataset.id === selectedId ? 0 : -1;
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
    detail.innerHTML = materialDetail(material, false);
    bindDetail(detail);
    drawConnections(material);
    requestAnimationFrame(() => centerMaterialInViewport(material.id));

    if (openSheet && matchMedia("(max-width:1160px)").matches) {
      sheetContent.innerHTML = materialDetail(material, true);
      bindDetail(sheetContent);
      if (!sheet.open) sheet.showModal();
    }
    announce(`${material.name}. ${material.review.label}.`);
    if (pushHash) setHash(`#material-${material.id}`, true);
  }

  function selectForm(id, options={}) {
    const {pushHash=false, openSheet=true} = options;
    const form = formById[id];
    if (!form) return;

    const parentIds = form.relationships
      .map(rel => byName[rel.mineral]?.id)
      .filter(Boolean);
    field.classList.add("form-mode");
    nodes.forEach(node => node.classList.toggle("related-parent", parentIds.includes(node.dataset.id)));
    if (parentIds.length) updateNodeState(parentIds[0]);

    if (matchMedia("(min-width:1161px)").matches) {
      detail.innerHTML = formDetail(form, false);
      bindDetail(detail);
    } else if (openSheet) {
      sheetContent.innerHTML = formDetail(form, true);
      bindDetail(sheetContent);
      if (!sheet.open) sheet.showModal();
    }
    announce(`${form.name}. ${form.review?.label || "Public context"}.`);
    if (pushHash) setHash(`#form-${form.id}`, true);
  }

  function restoreFromHash({initial=false}={}) {
    const hash = location.hash;

    if (!hash.startsWith("#material-") && !hash.startsWith("#form-") && sheet.open) {
      sheet.close();
    }
    if (hash === "#indexPanel") {
      setAtlasView("index", {focus:false, scroll:false});
    } else if (!hash.startsWith("#indexPanel")) {
      setAtlasView("constellation", {focus:false, scroll:false});
    }

    if (hash.startsWith("#material-")) {
      const id = hash.slice(10);
      if (byId[id]) {
        selectMaterial(id, {pushHash:false, openSheet:true});
        return;
      }
    }

    if (hash.startsWith("#form-")) {
      const id = hash.slice(6);
      if (formById[id]) {
        selectForm(id, {pushHash:false, openSheet:true});
        return;
      }
    }

    // Critical R6.2 correction:
    // populate the default Gallium context without covering the first mobile viewport.
    if (!hash || hash === "#atlas") {
      selectMaterial("gallium", {pushHash:false, openSheet:false});
    } else if (initial) {
      selectMaterial("gallium", {pushHash:false, openSheet:false});
    }
  }

  function applyLens() {
    const active = activeLens === "all" ? null : lensMap[activeLens];
    let count = 0;
    nodes.forEach(node => {
      const material = byId[node.dataset.id];
      const hit = !active || material.lenses.includes(activeLens);
      if (hit) count += 1;
      node.classList.toggle("dim", Boolean(active) && !hit);
      node.classList.toggle("lens-hit", Boolean(active) && hit);
      if (active) node.style.setProperty("--active-lens", active.color);
      else node.style.removeProperty("--active-lens");
    });
    lensCount.textContent = active ? `${count} connected materials` : "60 materials";
    drawConnections(byId[selectedId]);
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
    svg.innerHTML = "";
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
    activeResult = -1;
    if (!query) {
      results.hidden = true;
      search.setAttribute("aria-expanded", "false");
      return;
    }

    const items = [
      ...materials.map(item => ({...item, type:"mineral"})),
      ...forms.map(item => ({...item, type:"form"}))
    ]
      .map(item => ({item, score:score(item, query)}))
      .filter(entry => entry.score < 99)
      .sort((a,b) => a.score - b.score || a.item.name.localeCompare(b.item.name))
      .slice(0,12)
      .map(entry => entry.item);

    results.innerHTML = items.length
      ? items.map(item => `<button type="button" class="search-result" role="option" aria-selected="false" data-result-type="${item.type}" data-result-id="${esc(item.id)}"><span class="r-symbol">${esc(item.symbol)}</span><span><strong>${esc(item.name)}</strong><small>${esc(entityKindLabel(item))}</small></span><span>${esc(entityShortLabel(item))}</span></button>`).join("")
      : `<div class="search-result"><span class="r-symbol">0</span><span><strong>No public result</strong><small>Try another official mineral or material system.</small></span><span></span></div>`;

    results.hidden = false;
    search.setAttribute("aria-expanded", "true");
    results.querySelectorAll("button").forEach(button =>
      button.addEventListener("click", () => activateResult(button))
    );
  }

  function activateResult(button) {
    results.hidden = true;
    search.setAttribute("aria-expanded", "false");
    search.value = "";

    activeLens = "all";
    lensButtons.forEach(item => {
      const on = item.dataset.lens === "all";
      item.classList.toggle("active", on);
      item.setAttribute("aria-pressed", String(on));
    });
    applyLens();

    if (button.dataset.resultType === "mineral") {
      selectMaterial(button.dataset.resultId, {pushHash:true, openSheet:true});
    } else {
      selectForm(button.dataset.resultId, {pushHash:true, openSheet:true});
    }
  }

  function moveResult(delta) {
    const options = [...results.querySelectorAll("button[role=option]")];
    if (!options.length) return;
    activeResult = (activeResult + delta + options.length) % options.length;
    options.forEach((option,index) =>
      option.setAttribute("aria-selected", String(index === activeResult))
    );
    options[activeResult].scrollIntoView({block:"nearest"});
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
      activeResult = -1;
    }
  });

  document.querySelectorAll(".form-card [data-form-id]").forEach(button =>
    button.addEventListener("click", event => {
      event.preventDefault();
      selectForm(button.dataset.formId, {pushHash:true, openSheet:true});
    })
  );

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
    if (showIndex && scroll) index.scrollIntoView({block:"start",behavior:"smooth"});
    announce(showIndex ? "Precision Index view." : "Strategic Constellation view.");
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
  addEventListener("resize", () => requestAnimationFrame(() => drawConnections(byId[selectedId])));

  document.documentElement.classList.add("js-ready");
  bindDetail(detail);
  applyLens();
  restoreFromHash({initial:true});
  enableConstellationKeyboard();
})();