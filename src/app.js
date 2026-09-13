/* ============================================================
   MYSTERY DECK — app logic (no dependencies, no build step)
   ============================================================ */
(function () {
  "use strict";

  var DATA = JSON.parse(document.getElementById("deck-data").textContent);
  var byId = Object.create(null);
  DATA.forEach(function (d) { byId[d.id] = d; });

  var RM = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var FINE = window.matchMedia("(hover:hover) and (pointer:fine)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var RAR_RGB = {
    Common: "111,215,255", Uncommon: "157,255,90", Rare: "180,120,255",
    Epic: "255,79,216", Legendary: "255,196,77"
  };
  var RAR_ORDER = ["Legendary", "Epic", "Rare", "Uncommon", "Common"];
  var RANK = { Legendary: 0, Epic: 1, Rare: 2, Uncommon: 3, Common: 4 };

  var grid = $("#grid"), burstEl = $("#burst"), loader = $("#loader"), sentinel = $("#sentinel");

  /* ---------------------------------------------------------- storage */
  var store = {
    get: function (k, fb) { try { var v = localStorage.getItem(k); return v === null ? fb : JSON.parse(v); } catch (e) { return fb; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode / sandbox */ } }
  };
  var revealed = new Set(store.get("mysterydeck.revealed.v1", []));
  var soundOn = !!store.get("mysterydeck.sound.v1", false);

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  var pad3 = function (n) { return String(n).padStart(3, "0"); };

  /* ---------------------------------------------------------- card markup */
  function cardHTML(it) {
    var rv = revealed.has(it.id);
    var bars = "";
    for (var k = 1; k <= 5; k++) bars += '<i class="' + (k <= it.d ? "on" : "") + '"></i>';
    var tags = it.tags.map(function (t) { return "<span>" + esc(t) + "</span>"; }).join("");
    var fx = '<div class="spot"></div><div class="shine"></div><div class="beam"></div>' +
      '<span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span>';

    return '' +
      '<article class="card r-' + it.r + (rv ? " revealed in" : "") + '" data-id="' + it.id + '" data-rar="' + it.r +
      '" tabindex="0" role="button" style="--spark:' + it.spark + '%" aria-label="' +
      (rv ? esc(it.t) : "Sealed card " + it.id + " — activate to reveal") + '">' +
      '<div class="inner">' +

      /* sealed */
      '<div class="face sealed">' + fx +
      '<div class="foil"></div><div class="circuit"></div>' +
      '<div class="seal-top"><span class="seal-tag">Sealed</span><span>No. ' + pad3(it.n) + '</span></div>' +
      '<div class="rune"><svg viewBox="0 0 100 100" aria-hidden="true">' +
      '<circle class="ring" cx="50" cy="50" r="46"/><circle class="ring2" cx="50" cy="50" r="38"/>' +
      '<polygon class="hex" points="50,9 85,29.5 85,70.5 50,91 15,70.5 15,29.5"/></svg><span class="q">?</span></div>' +
      '<div class="seal-name">Unknown concept</div>' +
      '<div class="seal-hint">click to unseal</div>' +
      '<div class="seal-bottom"><span>cat ·····</span><span class="gem"><i class="dia"></i>' + it.r + '</span></div>' +
      '</div>' +

      /* open */
      '<div class="face open">' + fx +
      '<div class="o-top"><span>No. ' + pad3(it.n) + '</span><span class="rar"><i class="dia"></i>' + it.r + '</span></div>' +
      '<div class="o-cat">' + esc(it.c) + '</div>' +
      '<h3 class="o-title">' + (rv ? esc(it.t) : "") + '</h3>' +
      '<div class="o-rule"></div>' +
      '<p class="o-blurb">' + (rv ? esc(it.b) : "") + '</p>' +
      '<div class="o-tags">' + tags + '</div>' +
      '<div class="o-meta">' +
      '<div class="mrow"><span>Difficulty</span><span class="bars">' + bars + '</span></div>' +
      '<div class="mrow"><span>MVP build</span><b>' + esc(it.w) + '</b></div>' +
      '<div class="mrow"><span>Spark score</span><span class="mval"><b>' + it.spark + '%</b><i class="meter"><b></b></i></span></div>' +
      '</div></div>' +

      '</div><i class="shock"></i></article>';
  }

  /* ---------------------------------------------------------- filtering + render */
  var state = { q: "", cat: "", rar: "", diff: "", seal: "", sort: "id" };
  var view = [], rendered = 0, CHUNK = 48;

  function computeView() {
    var q = state.q.trim().toLowerCase();
    var out = DATA.filter(function (d) {
      if (state.cat && d.c !== state.cat) return false;
      if (state.rar && d.r !== state.rar) return false;
      if (state.diff && String(d.d) !== state.diff) return false;
      if (state.seal === "sealed" && revealed.has(d.id)) return false;
      if (state.seal === "revealed" && !revealed.has(d.id)) return false;
      if (q) {
        var hay = (d.t + " " + d.b + " " + d.c + " " + d.tags.join(" ") + " " + d.id + " " + d.r).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
    var s = state.sort;
    out.sort(function (a, b) {
      if (s === "rarity") return RANK[a.r] - RANK[b.r] || a.n - b.n;
      if (s === "hard") return b.d - a.d || a.n - b.n;
      if (s === "easy") return a.d - b.d || a.n - b.n;
      if (s === "spark") return b.spark - a.spark || a.n - b.n;
      if (s === "shuffle") return (a._s || 0) - (b._s || 0);
      return a.n - b.n;
    });
    return out;
  }

  function applyFilters(keepScroll) {
    if (state.sort === "shuffle") DATA.forEach(function (d) { d._s = Math.random(); });
    view = computeView();
    rendered = 0;
    grid.innerHTML = "";
    if (!view.length) {
      grid.innerHTML = '<div class="empty"><b>⌀</b>no cards match that signal</div>';
      loader.hidden = true;
    } else {
      renderChunk();
    }
    $("#shown").textContent = view.length;
    if (!keepScroll) { /* keep position */ }
  }

  function renderChunk() {
    if (rendered >= view.length) { loader.hidden = true; return; }
    var end = Math.min(rendered + CHUNK, view.length);
    var html = "";
    for (var i = rendered; i < end; i++) html += cardHTML(view[i]);
    grid.insertAdjacentHTML("beforeend", html);
    rendered = end;
    loader.hidden = rendered >= view.length;
    observeNew();
  }

  /* entrance observer */
  var inObs = new IntersectionObserver(function (entries) {
    var n = 0;
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target;
      inObs.unobserve(el);
      if (RM) { el.classList.add("in"); return; }
      var d = Math.min(n++ * 26, 420);
      el.style.transitionDelay = d + "ms";
      el.classList.add("in");
      setTimeout(function () { el.style.transitionDelay = ""; }, 700 + d);
    });
  }, { rootMargin: "80px 0px" });

  function observeNew() {
    $$(".card:not(.in)", grid).forEach(function (c) { inObs.observe(c); });
  }

  /* infinite render sentinel */
  new IntersectionObserver(function (entries) {
    if (entries[0].isIntersecting && rendered < view.length) renderChunk();
  }, { rootMargin: "900px 0px" }).observe(sentinel);

  /* ---------------------------------------------------------- scramble / decrypt */
  var GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<>/\\[]{}=+*^?#§%$&@!";
  var active = new Set(), sRaf = null;
  function scramble(el, text, dur) {
    if (!el) return;
    if (RM) { el.textContent = text; return; }
    active.forEach(function (s) { if (s.el === el) active.delete(s); });
    var st = { el: el, text: text, dur: dur || 640, t0: performance.now() };
    active.add(st);
    if (!sRaf) sRaf = requestAnimationFrame(tickScramble);
  }
  function tickScramble(now) {
    active.forEach(function (s) {
      var p = Math.min(1, (now - s.t0) / s.dur);
      var cut = Math.floor(p * p * s.text.length) + Math.floor(p * 4);
      var out = "";
      for (var i = 0; i < s.text.length; i++) {
        var ch = s.text[i];
        out += (i < cut || ch === " ") ? ch : GLYPHS[(Math.random() * GLYPHS.length) | 0];
      }
      s.el.textContent = out;
      if (p >= 1) { s.el.textContent = s.text; active.delete(s); }
    });
    sRaf = active.size ? requestAnimationFrame(tickScramble) : null;
  }

  /* ---------------------------------------------------------- particles / burst */
  function burst(x, y, rgb, n) {
    if (RM) return;
    var f = document.createDocumentFragment(), i, p, a, d;
    for (i = 0; i < (n || 14); i++) {
      p = document.createElement("i"); p.className = "pt";
      a = Math.random() * Math.PI * 2; d = 55 + Math.random() * 165;
      p.style.cssText = "left:" + x + "px;top:" + y + "px;--dx:" + (Math.cos(a) * d).toFixed(1) +
        "px;--dy:" + (Math.sin(a) * d).toFixed(1) + "px;--c:rgb(" + rgb + ");--dur:" +
        (560 + Math.random() * 620) + "ms;width:" + (3 + Math.random() * 4).toFixed(1) + "px;height:" + (3 + Math.random() * 4).toFixed(1) + "px";
      p.addEventListener("animationend", function () { this.remove(); });
      f.appendChild(p);
    }
    var r = document.createElement("i"); r.className = "ring";
    r.style.cssText = "left:" + x + "px;top:" + y + "px;width:300px;height:300px;--c:rgb(" + rgb + ")";
    r.addEventListener("animationend", function () { this.remove(); });
    f.appendChild(r);
    burstEl.appendChild(f);
  }
  function flash() {
    var f = $("#flash");
    f.classList.remove("go"); void f.offsetWidth; f.classList.add("go");
    setTimeout(function () { f.classList.remove("go"); }, 700);
  }
  function shake() {
    document.body.classList.add("shake");
    setTimeout(function () { document.body.classList.remove("shake"); }, 460);
  }

  /* ---------------------------------------------------------- audio (synth, opt-in) */
  var AC = null;
  var NOTE = { Common: 523.25, Uncommon: 659.25, Rare: 783.99, Epic: 987.77, Legendary: 1318.5 };
  function blip(rar, down) {
    if (!soundOn) return;
    try {
      AC = AC || new (window.AudioContext || window.webkitAudioContext)();
      if (AC.state === "suspended") AC.resume();
      var t = AC.currentTime, f = NOTE[rar] || 600;
      var o = AC.createOscillator(), g = AC.createGain(), o2 = AC.createOscillator(), g2 = AC.createGain();
      o.type = "triangle"; o.frequency.setValueAtTime(down ? f * 1.5 : f * .6, t);
      o.frequency.exponentialRampToValueAtTime(down ? f * .6 : f * 1.5, t + .16);
      g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.09, t + .012);
      g.gain.exponentialRampToValueAtTime(.0001, t + .34);
      o2.type = "sine"; o2.frequency.setValueAtTime(f * 2, t);
      g2.gain.setValueAtTime(.0001, t); g2.gain.exponentialRampToValueAtTime(.035, t + .01);
      g2.gain.exponentialRampToValueAtTime(.0001, t + .22);
      o.connect(g).connect(AC.destination); o2.connect(g2).connect(AC.destination);
      o.start(t); o2.start(t); o.stop(t + .36); o2.stop(t + .24);
    } catch (e) { /* audio unavailable */ }
  }

  /* ---------------------------------------------------------- reveal */
  function fill(card, it) {
    var t = $(".o-title", card), b = $(".o-blurb", card);
    if (t && !t.textContent) t.textContent = it.t;
    if (b && !b.textContent) b.textContent = it.b;
    card.setAttribute("aria-label", it.t);
  }

  function reveal(card, opts) {
    opts = opts || {};
    var it = byId[card.dataset.id];
    if (!it) return;
    var wasNew = !card.classList.contains("revealed");
    card.classList.add("revealed", "in");
    revealed.add(it.id);

    if (opts.instant || RM) {
      fill(card, it);
    } else {
      var t = $(".o-title", card), b = $(".o-blurb", card);
      scramble(t, it.t, 700);
      setTimeout(function () { scramble(b, it.b, 900); }, 110);
      card.setAttribute("aria-label", it.t);
    }
    if (wasNew && !opts.instant && !RM) {
      card.classList.add("pop");
      setTimeout(function () { card.classList.remove("pop"); }, 950);
      var r = card.getBoundingClientRect();
      var big = it.r === "Legendary";
      burst(r.left + r.width / 2, r.top + r.height / 2, RAR_RGB[it.r], big ? 34 : (it.r === "Epic" ? 22 : 14));
      if (big && !opts.quiet) { flash(); shake(); }
      blip(it.r, false);
    }
    if (!opts.nosave) store.set("mysterydeck.revealed.v1", Array.from(revealed));
    queueStats();
  }

  function reseal(card) {
    var it = byId[card.dataset.id];
    card.classList.remove("revealed", "pop");
    var t = $(".o-title", card), b = $(".o-blurb", card);
    if (t) t.textContent = "";
    if (b) b.textContent = "";
    if (it) card.setAttribute("aria-label", "Sealed card " + it.id + " — activate to reveal");
  }

  /* ---------------------------------------------------------- grid interaction */
  var tiltCard = null;
  function resetTilt(c) {
    if (!c) return;
    c.style.removeProperty("--rx"); c.style.removeProperty("--ry");
  }
  if (FINE && !RM) {
    grid.addEventListener("pointermove", function (e) {
      var card = e.target.closest ? e.target.closest(".card") : null;
      if (card !== tiltCard) { resetTilt(tiltCard); tiltCard = card; }
      if (!card) return;
      var r = card.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
      card.style.setProperty("--ry", ((px - .5) * 15).toFixed(2) + "deg");
      card.style.setProperty("--rx", ((.5 - py) * 13).toFixed(2) + "deg");
      card.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
      card.style.setProperty("--my", (py * 100).toFixed(1) + "%");
    }, { passive: true });
    grid.addEventListener("pointerleave", function () { resetTilt(tiltCard); tiltCard = null; });
  }

  function activate(card) {
    if (!card) return;
    if (card.classList.contains("revealed")) {
      /* re-decrypt on demand */
      var it = byId[card.dataset.id];
      if (it && !RM) { scramble($(".o-title", card), it.t, 480); blip(it.r, true); }
      return;
    }
    reveal(card);
  }
  grid.addEventListener("click", function (e) { activate(e.target.closest(".card")); });
  grid.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var c = e.target.closest(".card");
    if (!c) return;
    e.preventDefault(); activate(c);
  });

  /* ---------------------------------------------------------- stats */
  var stOpen = $("#stOpen"), stSealed = $("#stSealed"), stLeg = $("#stLeg");
  var dockCount = $("#dockCount"), dockBar = $("#dockBar"), dockPct = $("#dockPct");
  var statsQueued = false;
  function queueStats() {
    if (statsQueued) return;
    statsQueued = true;
    requestAnimationFrame(function () { statsQueued = false; updateStats(); });
  }
  function updateStats() {
    var open = revealed.size, total = DATA.length;
    stOpen.textContent = open;
    stSealed.textContent = total - open;
    dockCount.textContent = open + " / " + total;
    var pct = total ? (open / total) * 100 : 0;
    dockBar.style.width = pct.toFixed(2) + "%";
    dockPct.textContent = pct.toFixed(pct >= 10 ? 0 : 1) + "%";
  }

  /* ---------------------------------------------------------- toast */
  var toastEl = $("#toast"), toastT = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("on");
    clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.classList.remove("on"); }, 2100);
  }

  /* ---------------------------------------------------------- chips + legend */
  var cats = [];
  DATA.forEach(function (d) { if (cats.indexOf(d.c) === -1) cats.push(d.c); });
  cats.sort();
  var catBox = $("#catChips"), rarBox = $("#rarChips");
  catBox.innerHTML = '<button class="chip on" data-cat="">All ideas</button>' +
    cats.map(function (c) {
      var n = DATA.filter(function (d) { return d.c === c; }).length;
      return '<button class="chip" data-cat="' + esc(c) + '">' + esc(c) + " · " + n + "</button>";
    }).join("");
  rarBox.innerHTML = '<button class="chip on" data-rar="">All rarities</button>' +
    RAR_ORDER.map(function (r) {
      var n = DATA.filter(function (d) { return d.r === r; }).length;
      return '<button class="chip r-' + r + '" data-rar="' + r + '" style="--rc:rgb(' + RAR_RGB[r] + ')"><i class="dia"></i> ' + r + " · " + n + "</button>";
    }).join("");
  $("#legend").innerHTML = RAR_ORDER.map(function (r) {
    var n = DATA.filter(function (d) { return d.r === r; }).length;
    return '<span class="g" style="--rc:rgb(' + RAR_RGB[r] + ')"><i class="dia"></i><b>' + r + "</b> ×" + n + "</span>";
  }).join("");
  $("#stLeg").textContent = DATA.filter(function (d) { return d.r === "Legendary"; }).length;
  $("#stCat").textContent = cats.length;

  catBox.addEventListener("click", function (e) {
    var b = e.target.closest(".chip"); if (!b) return;
    $$(".chip", catBox).forEach(function (c) { c.classList.remove("on"); });
    b.classList.add("on"); state.cat = b.dataset.cat; applyFilters();
  });
  rarBox.addEventListener("click", function (e) {
    var b = e.target.closest(".chip"); if (!b) return;
    $$(".chip", rarBox).forEach(function (c) { c.classList.remove("on"); });
    b.classList.add("on"); state.rar = b.dataset.rar; applyFilters();
  });

  /* ---------------------------------------------------------- controls */
  var qEl = $("#q"), qt = null;
  qEl.addEventListener("input", function () {
    clearTimeout(qt);
    qt = setTimeout(function () { state.q = qEl.value; applyFilters(); }, 130);
  });
  $("#diff").addEventListener("change", function (e) { state.diff = e.target.value; applyFilters(); });
  $("#state").addEventListener("change", function (e) { state.seal = e.target.value; applyFilters(); });
  $("#sort").addEventListener("change", function (e) { state.sort = e.target.value; applyFilters(); });

  $("#openAll").addEventListener("click", function () { unsealAll(); });
  $("#reseal").addEventListener("click", function () {
    var had = revealed.size;
    revealed.clear();
    store.set("mysterydeck.revealed.v1", []);
    applyFilters();
    updateStats();
    blip("Common", true);
    toast(had ? "deck re-sealed · " + had + " cards hidden again" : "deck already sealed");
  });

  function unsealAll() {
    var targets = view.length ? view : DATA;
    targets.forEach(function (d) { revealed.add(d.id); });
    store.set("mysterydeck.revealed.v1", Array.from(revealed));
    var cards = $$(".card:not(.revealed)", grid);
    cards.forEach(function (c, i) {
      setTimeout(function () { reveal(c, { instant: true, quiet: true, nosave: true }); }, RM ? 0 : Math.min(i * 7, 1400));
    });
    if (state.seal) setTimeout(applyFilters, RM ? 0 : 900);
    updateStats();
    blip("Legendary", false);
    toast(targets.length + " seals broken");
  }

  /* sound toggle */
  var soundBtn = $("#sound");
  function paintSound() {
    soundBtn.setAttribute("aria-pressed", String(soundOn));
    soundBtn.textContent = soundOn ? "♪ On" : "♪ Off";
  }
  soundBtn.addEventListener("click", function () {
    soundOn = !soundOn; store.set("mysterydeck.sound.v1", soundOn); paintSound();
    if (soundOn) blip("Rare", false);
    toast(soundOn ? "audio online" : "audio muted");
  });
  paintSound();

  /* ---------------------------------------------------------- deal modal */
  var modal = $("#modal"), dealCard = $("#dealCard"), dealTitle = $("#dealTitle"), dealSub = $("#dealSub");
  var lastDeal = null;

  function pickRandom() {
    var pool = view.length ? view.slice() : DATA.slice();
    var sealedPool = pool.filter(function (d) { return !revealed.has(d.id); });
    var src = sealedPool.length ? sealedPool : pool;
    var pick, guard = 0;
    do { pick = src[(Math.random() * src.length) | 0]; guard++; }
    while (pick && pick.id === lastDeal && src.length > 1 && guard < 12);
    return pick;
  }

  function deal() {
    var it = pickRandom();
    if (!it) { toast("no cards match"); return; }
    lastDeal = it.id;
    modal.classList.add("on");
    dealTitle.textContent = "Dealing…";
    dealSub.textContent = "random pull · no. " + pad3(it.n);
    dealCard.innerHTML = cardHTML(it);
    var card = $(".card", dealCard);
    if (!revealed.has(it.id)) {
      card.classList.remove("revealed");
      setTimeout(function () {
        reveal(card, {});
        syncGrid(it.id);
        dealTitle.textContent = it.r + " pull";
        dealSub.textContent = it.c + " · mvp " + it.w + " · spark " + it.spark + "%";
      }, RM ? 60 : 780);
    } else {
      card.classList.add("revealed", "in");
      fill(card, it);
      dealTitle.textContent = it.r + " pull";
      dealSub.textContent = "already unsealed";
    }
    blip(it.r, false);
  }
  function syncGrid(id) {
    var c = $('.card[data-id="' + id + '"]', grid);
    if (c && !c.classList.contains("revealed")) { c.classList.add("revealed", "in"); fill(c, byId[id]); }
  }
  function closeModal() { modal.classList.remove("on"); }
  $("#deal").addEventListener("click", deal);
  $("#dealAgain").addEventListener("click", deal);
  dealCard.addEventListener("click", function (e) { activate(e.target.closest(".card")); });
  $$("[data-close]", modal).forEach(function (el) { el.addEventListener("click", closeModal); });

  /* ---------------------------------------------------------- keyboard */
  document.addEventListener("keydown", function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement && document.activeElement.tagName);
    if (e.key === "Escape") { closeModal(); if (typing) document.activeElement.blur(); return; }
    if (typing) return;
    if (e.key === "/") { e.preventDefault(); qEl.focus(); qEl.select(); }
    else if (e.key === "r" || e.key === "R") { e.preventDefault(); deal(); }
    else if (e.key === "u" || e.key === "U") { e.preventDefault(); unsealAll(); }
    else if (e.key === "s" || e.key === "S") { soundBtn.click(); }
  });

  /* ---------------------------------------------------------- ticker */
  var TICK = ["500 sealed web-app ideas", "hover to charge", "click to break the seal", "14 categories",
    "5 rarity tiers", "17 legendary pulls", "no backend, no accounts, no tracking", "one html file",
    "steal an idea", "ship it this weekend", "the deck remembers what you unsealed", "press R for a random pull"];
  var tickHTML = TICK.map(function (t) { return "<span>" + esc(t) + ' <i>◆</i></span>'; }).join("");
  $("#tickerTrack").innerHTML = tickHTML + tickHTML;

  /* ---------------------------------------------------------- particle field */
  (function particles() {
    if (RM) return;
    var c = $("#fx"), ctx = c.getContext("2d");
    if (!ctx) return;
    var W = 0, H = 0, DPR = 1, pts = [], mouse = { x: -9999, y: -9999 }, raf = null, live = true;
    function size() {
      DPR = Math.min(2, window.devicePixelRatio || 1);
      W = c.width = Math.floor(innerWidth * DPR); H = c.height = Math.floor(innerHeight * DPR);
      c.style.width = innerWidth + "px"; c.style.height = innerHeight + "px";
      var target = innerWidth < 700 ? 26 : (innerWidth < 1200 ? 46 : 68);
      pts = [];
      for (var i = 0; i < target; i++) pts.push(mk());
    }
    function mk() {
      return {
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - .5) * .22 * DPR, vy: (Math.random() - .5) * .22 * DPR,
        r: (Math.random() * 1.5 + .5) * DPR,
        h: Math.random() < .62 ? "37,232,255" : (Math.random() < .6 ? "255,47,179" : "157,107,255")
      };
    }
    function frame() {
      if (!live) return;
      ctx.clearRect(0, 0, W, H);
      var i, j, p, q2, dx, dy, d2, lim = 132 * DPR;
      for (i = 0; i < pts.length; i++) {
        p = pts[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < -20) p.x = W + 20; if (p.x > W + 20) p.x = -20;
        if (p.y < -20) p.y = H + 20; if (p.y > H + 20) p.y = -20;
        dx = p.x - mouse.x * DPR; dy = p.y - mouse.y * DPR; d2 = dx * dx + dy * dy;
        if (d2 < (140 * DPR) * (140 * DPR) && d2 > 1) {
          var f = (1 - d2 / ((140 * DPR) * (140 * DPR))) * .035;
          p.vx += dx * f * .012; p.vy += dy * f * .012;
          p.vx *= .995; p.vy *= .995;
        }
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283);
        ctx.fillStyle = "rgba(" + p.h + ",.72)"; ctx.fill();
      }
      ctx.lineWidth = .6 * DPR;
      for (i = 0; i < pts.length; i++) {
        for (j = i + 1; j < pts.length; j++) {
          p = pts[i]; q2 = pts[j];
          dx = p.x - q2.x; dy = p.y - q2.y; d2 = dx * dx + dy * dy;
          if (d2 < lim * lim) {
            var a = (1 - Math.sqrt(d2) / lim) * .2;
            ctx.strokeStyle = "rgba(120,200,255," + a.toFixed(3) + ")";
            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q2.x, q2.y); ctx.stroke();
          }
        }
      }
      raf = requestAnimationFrame(frame);
    }
    function start() { if (!raf && live) raf = requestAnimationFrame(frame); }
    function stop() { if (raf) cancelAnimationFrame(raf); raf = null; }
    size(); start();
    var rt = null;
    window.addEventListener("resize", function () {
      clearTimeout(rt); rt = setTimeout(function () { size(); }, 180);
    });
    window.addEventListener("pointermove", function (e) { mouse.x = e.clientX; mouse.y = e.clientY; }, { passive: true });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) { live = false; stop(); } else { live = true; start(); }
    });
  })();

  /* cursor glow */
  (function () {
    var g = $("#cglow"); if (!g || !FINE) return;
    var tx = 0, ty = 0, cx = 0, cy = 0, on = false;
    window.addEventListener("pointermove", function (e) { tx = e.clientX; ty = e.clientY; if (!on) { on = true; loop(); } }, { passive: true });
    function loop() {
      cx += (tx - cx) * .14; cy += (ty - cy) * .14;
      g.style.transform = "translate3d(" + cx.toFixed(1) + "px," + cy.toFixed(1) + "px,0)";
      if (Math.abs(tx - cx) > .4 || Math.abs(ty - cy) > .4) requestAnimationFrame(loop); else on = false;
    }
  })();

  /* ---------------------------------------------------------- counters */
  function countUp(el, to, dur) {
    if (RM) { el.textContent = to; return; }
    var t0 = performance.now();
    (function step(now) {
      var p = Math.min(1, (now - t0) / (dur || 1100));
      el.textContent = Math.round(to * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    })(t0);
  }

  /* ---------------------------------------------------------- boot */
  (function boot() {
    var box = $("#boot"), lines = $("#bootLines");
    var L = [
      "> initializing deck protocol…",
      "> scanning archive: <b>500 cards detected</b>",
      "> assigning rarity signatures…",
      "> encrypting concepts <b>[SEALED]</b>",
      "> ready — break something."
    ];
    if (RM) { finish(); return; }
    var i = 0;
    (function next() {
      if (i >= L.length) { setTimeout(finish, 320); return; }
      var d = document.createElement("div");
      d.innerHTML = L[i++];
      d.style.animationDelay = "0ms";
      lines.appendChild(d);
      setTimeout(next, 240);
    })();
    var booted = false;
    function finish() {
      if (booted) return; booted = true;
      box.classList.add("done");
      setTimeout(function () { box.remove(); }, 700);
      countUp($("#stTotal"), DATA.length, 1200);
    }
    box.addEventListener("click", finish);
    document.addEventListener("keydown", function skip(e) {
      if (e.key === "Escape" || e.key === "Enter") { finish(); document.removeEventListener("keydown", skip); }
    });
  })();

  /* ---------------------------------------------------------- go */
  applyFilters();
  updateStats();
  if (revealed.size) setTimeout(function () { toast(revealed.size + " cards already unsealed"); }, 1900);

  /* expose a tiny debug hook */
  window.MYSTERY_DECK = { data: DATA, revealed: revealed, deal: deal, unsealAll: unsealAll };
})();
