/** Capture the actual saved Pyvis pages with an installed Chrome and no npm dependencies.
 * Run: node tools/capture_visualizations.mjs [path-to-chrome]
 * Uses a fresh temporary profile, never the user's browser profile.
 */
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const chromePath = process.argv[2] || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const output = join(root, 'evidence', 'screenshots');
const captures = [
  ['filtered-network', 'semantic-networks/visualizations/Filtered Semantic Network.html', 69, 82],
  ['filtered-network-root', 'semantic-networks_total/Filtered Semantic Network.html', 69, 82],
  ['filtered-network-expanded', 'semantic-networks_total/visualizations/Filtered Semantic Network.html', 194, 246],
  ['k-core-network', 'semantic-networks_total/visualizations/K-core Semantic Network(k=2).html', 278, 353],
  ['connected-event-network', 'semantic-networks_total/visualizations/Original Semantic Network of Connected Events.html', 1978, 2064],
];
const profile = await mkdtemp(join(dirname(root), '.kp-visual-capture-'));
const chrome = spawn(chromePath, [
  '--headless=new', '--remote-debugging-port=0', '--no-first-run',
  '--no-default-browser-check', '--disable-background-networking',
  '--disable-component-update', '--disable-sync', '--disk-cache-size=1',
  `--user-data-dir=${profile}`, 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });
let socket;
try {
  const endpoint = await new Promise((accept, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error('Chrome startup timed out')), 20000);
    chrome.once('error', error => { clearTimeout(timer); reject(error); });
    chrome.stderr.on('data', chunk => {
      log += chunk;
      const match = log.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) { clearTimeout(timer); accept(match[1]); }
    });
  });
  const port = new URL(endpoint).port;
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket = new WebSocket(targets.find(target => target.type === 'page').webSocketDebuggerUrl);
  await new Promise((accept, reject) => { socket.onopen = accept; socket.onerror = reject; });
  let sequence = 0;
  const pending = new Map();
  const errors = [];
  socket.onmessage = event => {
    const response = JSON.parse(event.data);
    if (response.method === 'Runtime.exceptionThrown') errors.push(response.params.exceptionDetails.text);
    if (!response.id) return;
    const callback = pending.get(response.id);
    if (!callback) return;
    pending.delete(response.id);
    clearTimeout(callback.timer);
    if (response.error) callback.reject(new Error(JSON.stringify(response.error)));
    else callback.accept(response.result);
  };
  const call = (method, params = {}) => new Promise((accept, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`${method} timed out`)); }, 140000);
    pending.set(id, { accept, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => {
    const result = await call('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
    return result.result.value;
  };
  await call('Page.enable');
  await call('Runtime.enable');
  await call('Emulation.setDeviceMetricsOverride', { width: 1600, height: 1600, deviceScaleFactor: 1, mobile: false });
  await mkdir(output, { recursive: true });
  const records = [];
  for (const [name, source, expectedNodes, expectedEdges] of captures) {
    const input = join(root, 'artifacts', 'original', source);
    const before = await readFile(input);
    errors.length = 0;
    await call('Page.navigate', { url: pathToFileURL(input).href });
    let ready = false;
    for (let attempt = 0; attempt < 100; attempt++) {
      ready = await evaluate('typeof network !== "undefined" && !!network && typeof nodes !== "undefined"');
      if (ready) break;
      await new Promise(accept => setTimeout(accept, 200));
    }
    if (!ready) throw new Error(`${name}: visualization did not initialize`);
    const rendering = await evaluate(`new Promise((accept, reject) => {
      const timeout = setTimeout(() => reject(new Error('Graph stabilization timed out')), 120000);
      network.once('stabilizationIterationsDone', () => {
        clearTimeout(timeout);
        network.stopSimulation();
        network.fit({animation: false});
        network.redraw();
        setTimeout(() => {
          const rect = document.getElementById('mynetwork').getBoundingClientRect();
          const bar = document.getElementById('loadingBar');
          accept({nodes: nodes.length, edges: edges.length,
            clip: {x: rect.x, y: rect.y, width: rect.width, height: rect.height, scale: 1},
            loadingHidden: !bar || getComputedStyle(bar).display === 'none',
            canvasCount: document.querySelectorAll('#mynetwork canvas').length});
        }, 800);
      });
      network.stabilize(1000);
    })`);
    if (rendering.nodes !== expectedNodes || rendering.edges !== expectedEdges || !rendering.loadingHidden || !rendering.canvasCount || errors.length) {
      throw new Error(`${name}: invalid render ${JSON.stringify({rendering, errors})}`);
    }
    const screenshot = await call('Page.captureScreenshot', { format: 'png', clip: rendering.clip, captureBeyondViewport: true });
    const png = Buffer.from(screenshot.data, 'base64');
    await writeFile(join(output, `${name}.png`), png);
    if (!before.equals(await readFile(input))) throw new Error('Original HTML unexpectedly changed');
    records.push({image: `evidence/screenshots/${name}.png`, source: `artifacts/original/${source}`,
      source_sha256: createHash('sha256').update(before).digest('hex'),
      image_sha256: createHash('sha256').update(png).digest('hex'),
      nodes: rendering.nodes, edges: rendering.edges, width: rendering.clip.width, height: rendering.clip.height});
    console.log(`Captured ${name}: ${rendering.nodes} nodes, ${rendering.edges} edges`);
  }
  await writeFile(join(output, 'capture-manifest.json'), JSON.stringify({
    method: 'Chrome screenshots of the original HTML pages. Original graph data and styling retained; physics stabilized for up to 1000 iterations, then stopped and fitted to the canvas. Layout positions may vary between captures.',
    captures: records,
  }, null, 2) + '\n');
} finally {
  socket?.close();
  chrome.kill('SIGTERM');
  if (chrome.exitCode === null) await new Promise(accept => { chrome.once('exit', accept); setTimeout(accept, 5000); });
  if (chrome.exitCode !== null || chrome.signalCode !== null) {
    await rm(profile, { recursive: true, force: true });
    console.log('Removed the isolated temporary Chrome profile.');
  } else {
    console.log('Chrome has not exited; its temporary profile was retained to avoid deleting active files.');
  }
}
