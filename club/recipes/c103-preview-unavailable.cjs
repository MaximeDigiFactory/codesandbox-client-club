const { chromium } = require("/browser/node_modules/playwright");
const crypto = require("crypto");

const PREVIEW_ORIGIN = "https://fixture-preview.artefacts.digiconseil.fr";
const FR_SNIPPET = "Aperçu indisponible";
const TECH_SNIPPET = "Could not connect";

async function testBlockedServiceWorker() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ serviceWorkers: "block" });
  const page = await context.newPage();
  const codesandbox = [];
  page.on("request", (r) => {
    try {
      const h = new URL(r.url()).hostname;
      if (/codesandbox\.io|csbops\.io/.test(h)) codesandbox.push(h);
    } catch (_) {}
  });
  await page.goto(`${PREVIEW_ORIGIN}/`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2500);
  const text = await page.locator("body").innerText();
  await browser.close();
  return {
    frMessage: text.includes(FR_SNIPPET) ? 1 : 0,
    techError: text.includes(TECH_SNIPPET) ? 1 : 0,
    codesandboxRequests: codesandbox.length,
  };
}

async function testNormalPreviewRelay() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const codesandbox = [];
  const onReq = (r) => {
    try {
      const h = new URL(r.url()).hostname;
      if (/codesandbox\.io|csbops\.io/.test(h)) codesandbox.push(h);
    } catch (_) {}
  };
  context.on("request", onReq);
  const relayErrors = [];
  const relay = await context.newPage();
  relay.on("console", (m) => {
    if (m.type() === "error") relayErrors.push(m.text());
  });
  const relayResp = await relay.goto(`${PREVIEW_ORIGIN}/__csb_relay/`, {
    waitUntil: "domcontentloaded",
  });
  await relay.waitForTimeout(1500);
  await browser.close();
  return {
    relayHttpOk: relayResp && relayResp.ok() ? 1 : 0,
    relaySwConsoleErrors: relayErrors.filter((e) =>
      /Failed to retrieve the worker instance/.test(e)
    ).length,
    codesandboxRequests: codesandbox.length,
  };
}

(async () => {
  const a = await testBlockedServiceWorker();
  const b = await testNormalPreviewRelay();
  console.log(JSON.stringify({ testA: a, testB: b }));
})();
