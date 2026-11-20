"use strict";

const assert = require("node:assert/strict");
const { execFileSync } = require("node:child_process");
const { once } = require("node:events");
const { mkdtemp, readFile, rm } = require("node:fs/promises");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const { chromium } = require("playwright");
const checkBoard = require("../../tests/board-browser.js");

const root = path.resolve(__dirname, "../..");

async function runBrowser(url) {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.setDefaultTimeout(10000);
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(url);
    const result = await checkBoard(page);
    assert.deepEqual(errors, [], "The board must not raise browser errors");
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
}

async function serveBoard(markup) {
  const server = http.createServer((request, response) => {
    if (request.url !== "/board.html") {
      response.writeHead(404).end();
      return;
    }
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
    response.end(markup);
  });
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  try {
    await runBrowser(`http://127.0.0.1:${server.address().port}/board.html`);
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  }
}

async function main() {
  const directory = await mkdtemp(path.join(os.tmpdir(), "badge-buddy-browser-"));
  try {
    const fixture = path.join(directory, "board.html");
    execFileSync(process.argv[2] || "python3", ["tests/support/browser_fixture.py", fixture], {
      cwd: root,
      stdio: "inherit",
    });
    await serveBoard(await readFile(fixture));
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
