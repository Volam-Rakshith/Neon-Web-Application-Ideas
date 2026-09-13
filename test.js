/* Smoke test: boots index.html in jsdom and exercises the deck. */
const fs = require("fs");
const { JSDOM, VirtualConsole } = require("jsdom");

const html = fs.readFileSync("index.html", "utf8");
const errors = [];
const cssNoise = /Could not parse CSS|Not implemented|Error: Could not|canvas/i;

const vc = new VirtualConsole();
vc.on("jsdomError", (e) => { if (!cssNoise.test(e.message)) errors.push("jsdomError: " + e.message + "\n" + (e.stack || "")); });
vc.on("error", (...a) => { const m = a.join(" "); if (!cssNoise.test(m)) errors.push("console.error: " + m); });

const dom = new JSDOM(html, {
  runScripts: "dangerously",
  pretendToBeVisual: true,
  url: "http://localhost:8080/",
  virtualConsole: vc,
  beforeParse(w) {
    w.matchMedia = (q) => ({
      media: q,
      matches: /hover:hover/.test(q) ? true : false,
      addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {},
    });
    const cbs = [];
    w.IntersectionObserver = class {
      constructor(cb) { this.cb = cb; this.els = []; cbs.push(this); }
      observe(el) { this.els.push(el); setTimeout(() => this.cb([{ target: el, isIntersecting: true }], this), 0); }
      unobserve(el) { this.els = this.els.filter((x) => x !== el); }
      disconnect() { this.els = []; }
    };
    w.HTMLCanvasElement.prototype.getContext = () => null;
    w.scrollTo = () => {};
  },
});

const w = dom.window, d = w.document;
const $ = (s, r) => (r || d).querySelector(s);
const $$ = (s, r) => [...(r || d).querySelectorAll(s)];
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log("  ✓ " + name); }
  else { fail++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); }
}
const click = (el) => el.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
const key = (k) => d.dispatchEvent(new w.KeyboardEvent("keydown", { key: k, bubbles: true }));

(async () => {
  console.log("\n— boot —");
  await wait(400);
  ok("boot overlay rendered lines", $("#bootLines") && $("#bootLines").children.length > 0);
  await wait(2200);
  ok("boot overlay removed", !$("#boot"), "still present");
  ok("data parsed: 500 cards", w.MYSTERY_DECK && w.MYSTERY_DECK.data.length === 500,
     w.MYSTERY_DECK ? w.MYSTERY_DECK.data.length : "no hook");

  console.log("\n— initial render —");
  await wait(600);
  const cards = $$("#grid .card");
  ok("grid rendered cards (progressive)", cards.length >= 48, "got " + cards.length);
  ok("ticker duplicated for loop", $("#tickerTrack").children.length === 24, "got " + $("#tickerTrack").children.length);
  ok("category chips built", $$("#catChips .chip").length === 15, "got " + $$("#catChips .chip").length);
  ok("rarity chips built", $$("#rarChips .chip").length === 6, "got " + $$("#rarChips .chip").length);
  ok("legend built", $$("#legend .g").length === 5);
  ok("stats: total counted up", $("#stTotal").textContent === "500", $("#stTotal").textContent);
  ok("stats: sealed = 500", $("#stSealed").textContent === "500", $("#stSealed").textContent);
  ok("sealed faces have no leaked title", $$("#grid .o-title").every((t) => t.textContent === ""));

  console.log("\n— scroll loading —");
  await wait(1500);
  ok("more chunks loaded on sentinel", $$("#grid .card").length > 48, "got " + $$("#grid .card").length);

  console.log("\n— reveal a card —");
  const first = $("#grid .card");
  const id = first.dataset.id;
  click(first);
  await wait(120);
  ok("card marked revealed", first.classList.contains("revealed"));
  ok("card got pop fx class", first.classList.contains("pop"));
  await wait(1400);
  const it = w.MYSTERY_DECK.data.find((x) => x.id === id);
  ok("title decrypted to real text", $(".o-title", first).textContent === it.t,
     JSON.stringify($(".o-title", first).textContent) + " vs " + JSON.stringify(it.t));
  ok("blurb filled", $(".o-blurb", first).textContent === it.b);
  ok("stats: unsealed = 1", $("#stOpen").textContent === "1", $("#stOpen").textContent);
  ok("dock progress updated", $("#dockCount").textContent === "1 / 500", $("#dockCount").textContent);
  ok("burst particles spawned", $("#burst").children.length > 0, "got " + $("#burst").children.length);
  ok("persisted to localStorage",
     (JSON.parse(w.localStorage.getItem("mysterydeck.revealed.v1") || "[]")).length === 1);

  console.log("\n— tilt + spotlight —");
  const pmove = (typeof w.PointerEvent === "function")
    ? new w.PointerEvent("pointermove", { bubbles: true, clientX: 100, clientY: 100 })
    : new w.MouseEvent("pointermove", { bubbles: true, clientX: 100, clientY: 100 });
  first.dispatchEvent(pmove);
  await wait(30);
  ok("tilt vars set on hover", first.style.getPropertyValue("--ry") !== "", first.getAttribute("style"));
  ok("spotlight vars set", first.style.getPropertyValue("--mx") !== "");

  console.log("\n— keyboard —");
  key("r");
  await wait(1200);
  ok("R opens deal modal", $("#modal").classList.contains("on"));
  ok("modal contains a card", !!$("#dealCard .card"));
  ok("modal card revealed", $("#dealCard .card").classList.contains("revealed"));
  ok("modal title text set", $("#dealTitle").textContent.toLowerCase().includes("pull"), $("#dealTitle").textContent);
  key("Escape");
  await wait(60);
  ok("Esc closes modal", !$("#modal").classList.contains("on"));
  key("/");
  ok("slash focuses search", d.activeElement === $("#q"));
  $("#q").blur();

  console.log("\n— filters —");
  $("#q").value = "coffee";
  $("#q").dispatchEvent(new w.Event("input", { bubbles: true }));
  await wait(350);
  const shown = parseInt($("#shown").textContent, 10);
  ok("search narrows results", shown > 0 && shown < 500, "shown=" + shown);
  ok("grid re-rendered to match", $$("#grid .card").length === shown || $$("#grid .card").length <= shown,
     "cards=" + $$("#grid .card").length);
  const allMatch = $$("#grid .card").every((c) => {
    const x = w.MYSTERY_DECK.data.find((y) => y.id === c.dataset.id);
    return (x.t + " " + x.b + " " + x.c + " " + x.tags.join(" ")).toLowerCase().includes("coffee");
  });
  ok("every visible card matches query", allMatch);
  $("#q").value = "";
  $("#q").dispatchEvent(new w.Event("input", { bubbles: true }));
  await wait(300);

  click($$("#catChips .chip")[3]);
  await wait(200);
  const catName = $$("#catChips .chip")[3].dataset.cat;
  ok("category chip filters (" + catName + ")", parseInt($("#shown").textContent, 10) > 0 &&
     $$("#grid .card").every((c) => $(".o-cat", c).textContent === catName));
  click($$("#catChips .chip")[0]);
  await wait(200);

  click($$("#rarChips .chip")[1]);
  await wait(200);
  ok("rarity chip filters (Legendary)", $$("#grid .card").every((c) => c.dataset.rar === "Legendary"));
  click($$("#rarChips .chip")[0]);
  await wait(150);

  $("#sort").value = "rarity";
  $("#sort").dispatchEvent(new w.Event("change", { bubbles: true }));
  await wait(200);
  const order = $$("#grid .card").map((c) => c.dataset.rar);
  ok("sort by rarity puts Legendary first", order[0] === "Legendary", order.slice(0, 3).join(","));
  $("#sort").value = "id";
  $("#sort").dispatchEvent(new w.Event("change", { bubbles: true }));
  await wait(200);

  $("#diff").value = "1";
  $("#diff").dispatchEvent(new w.Event("change", { bubbles: true }));
  await wait(200);
  ok("difficulty filter applies", parseInt($("#shown").textContent, 10) > 0 && parseInt($("#shown").textContent, 10) < 500);
  $("#diff").value = "";
  $("#diff").dispatchEvent(new w.Event("change", { bubbles: true }));
  await wait(200);

  console.log("\n— empty state —");
  $("#q").value = "zzzqqqxxx-nothing";
  $("#q").dispatchEvent(new w.Event("input", { bubbles: true }));
  await wait(320);
  ok("empty state shown", !!$("#grid .empty") && $$("#grid .card").length === 0);
  $("#q").value = "";
  $("#q").dispatchEvent(new w.Event("input", { bubbles: true }));
  await wait(320);

  console.log("\n— unseal / reseal —");
  click($("#openAll"));
  await wait(2000);
  ok("unseal all → 500 revealed", $("#stOpen").textContent === "500", $("#stOpen").textContent);
  ok("unseal all persisted", JSON.parse(w.localStorage.getItem("mysterydeck.revealed.v1")).length === 500);
  ok("deck progress 100%", $("#dockPct").textContent === "100%", $("#dockPct").textContent);
  click($("#reseal"));
  await wait(600);
  ok("reseal → 0 revealed", $("#stOpen").textContent === "0", $("#stOpen").textContent);
  ok("reseal cleared storage", JSON.parse(w.localStorage.getItem("mysterydeck.revealed.v1")).length === 0);
  ok("reseal cleared titles", $$("#grid .o-title").every((t) => t.textContent === ""));

  console.log("\n— sound toggle —");
  click($("#sound"));
  await wait(50);
  ok("sound toggles on", $("#sound").getAttribute("aria-pressed") === "true" && $("#sound").textContent.includes("On"));
  click($("#sound"));
  await wait(50);
  ok("sound toggles off", $("#sound").getAttribute("aria-pressed") === "false");

  console.log("\n— markup sanity —");
  ok("every card has 2 faces", $$("#grid .card").slice(0, 20).every((c) => $$(".face", c).length === 2));
  ok("every card has rune svg", $$("#grid .card").slice(0, 20).every((c) => !!$(".rune svg", c)));
  ok("both faces carry corner brackets + fx", $$("#grid .card").slice(0, 20).every((c) => $$(".corner", c).length === 8 && $$(".spot", c).length === 2 && $$(".beam", c).length === 2));
  ok("difficulty bars ≤ 5 lit", $$("#grid .bars").slice(0, 20).every((b) => $$(".on", b).length <= 5));
  ok("no undefined/NaN in DOM", !d.body.innerHTML.includes("undefined") && !d.body.innerHTML.includes("NaN"));

  console.log("\n— errors —");
  ok("no runtime errors", errors.length === 0, errors.slice(0, 4).join("\n"));

  console.log(`\n${pass} passed, ${fail} failed\n`);
  process.exit(fail ? 1 : 0);
})().catch((e) => { console.error("TEST CRASH", e); process.exit(2); });
