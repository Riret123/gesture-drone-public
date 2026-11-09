'use strict';
/* Read-only display contract. No publisher, control channel or flight authority. */
const TelemetryUI = (() => {
  const fields = ['acks','age','battery','deadman','mock','mode','schema'];
  const text = (value, minimum, maximum) => typeof value === 'string' &&
    [...value].length >= minimum && [...value].length <= maximum &&
    !/[\u0000-\u001f\u007f-\u009f\ud800-\udfff\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]/u.test(value);
  function normalize(data, elapsedSeconds, maxAge = 2) {
    if (!Number.isFinite(maxAge) || maxAge <= 0) throw Error('configuration');
    if (!Number.isFinite(elapsedSeconds) || elapsedSeconds < 0 ||
        data === null || Array.isArray(data) || typeof data !== 'object' ||
        Object.keys(data).sort().join('|') !== fields.join('|') ||
        data.schema !== 1 || typeof data.mock !== 'boolean' ||
        !Number.isFinite(data.age) || data.age < 0 ||
        !text(data.mode, 1, 64) || !Number.isFinite(data.battery) ||
        data.battery < 0 || data.battery > 100 || typeof data.deadman !== 'boolean' ||
        !Array.isArray(data.acks) || data.acks.length > 30 ||
        !data.acks.every(value => text(value, 0, 256))) return {status:'INVALID'};
    if (data.age + elapsedSeconds >= maxAge) return {status:'STALE'};
    return {status:data.mock ? 'MOCK DATA' : 'RECEIVED / UNVERIFIED',
      mode:data.mode, battery:data.battery, deadman:data.deadman,
      age:data.age + elapsedSeconds, acks:[...data.acks]};
  }
  async function readBounded(response, maxBytes = 16384) {
    if (!response.body || typeof response.body.getReader !== 'function') throw Error('stream unavailable');
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8', {fatal:true});
    let count = 0;
    let source = '';
    try {
      for (;;) {
        const {done, value} = await reader.read();
        if (done) break;
        count += value.byteLength;
        if (count > maxBytes) throw Error('body limit');
        source += decoder.decode(value, {stream:true});
      }
      source += decoder.decode();
      return JSON.parse(source);
    } finally {
      try { await reader.cancel(); } catch { /* already closed */ }
      reader.releaseLock();
    }
  }
  function start(document, fetcher, clock, schedule) {
    const get = id => document.getElementById(id);
    let acceptedRevision = 0;
    let visibilityEpoch = 0;
    function clear(status) {
      get('link').textContent = status;
      for (const id of ['mode','battery','deadman']) get(id).textContent = 'unknown';
      get('telemetry-note').textContent = 'Telemetry unavailable. Do not infer flight state from video.';
      if (get('history-note')) get('history-note').textContent = 'Retained history is stale; acknowledgements do not prove completed flight.';
    }
    if (typeof document.addEventListener === 'function') {
      document.addEventListener('visibilitychange', () => {
        visibilityEpoch += 1;
        acceptedRevision += 1;
        clear('OFFLINE / VISIBILITY CHANGED');
      });
    }
    async function poll() {
      const started = clock();
      const requestEpoch = visibilityEpoch;
      try {
        if (document.hidden === true) { clear('OFFLINE / HIDDEN'); return; }
        const response = await fetcher('/telemetry', {cache:'no-store', signal:AbortSignal.timeout(1500)});
        if (!response.ok) throw Error('HTTP');
        const data = await readBounded(response);
        if (requestEpoch !== visibilityEpoch || document.hidden === true) {
          clear('OFFLINE / VISIBILITY CHANGED'); return;
        }
        const view = normalize(data, (clock() - started) / 1000);
        if (!view.mode) { clear(view.status); return; }
        get('link').textContent = view.status;
        get('mode').textContent = view.mode;
        get('battery').textContent = view.battery.toFixed(0) + '%';
        get('deadman').textContent = view.deadman ? 'REPORTED PRESSED / NO CONTROL' : 'REPORTED RELEASED';
        get('telemetry-note').textContent = 'Conservative reported age: ' + view.age.toFixed(1) + ' s. Source honesty and FC acquisition are unverified.';
        const history = get('acks');
        if (history) {
          history.replaceChildren();
          for (const ack of [...view.acks].reverse()) {
            const row = document.createElement('li');
            row.textContent = ack;
            history.append(row);
          }
        }
        if (get('history-note')) get('history-note').textContent = 'At most 30 received entries. Service acceptance does not establish completed flight.';
        const revision = ++acceptedRevision;
        schedule(() => {
          if (revision === acceptedRevision) clear('STALE');
        }, Math.max(0, (2 - view.age) * 1000));
      } catch { clear('OFFLINE / INVALID'); }
      finally { schedule(poll, 1000); }
    }
    return poll();
  }
  return {normalize, readBounded, start};
})();
if (typeof module !== 'undefined' && module.exports) module.exports = TelemetryUI;
if (typeof document !== 'undefined') {
  TelemetryUI.start(document, fetch, () => performance.now(), setTimeout);
}
