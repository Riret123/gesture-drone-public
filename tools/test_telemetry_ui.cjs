/* Built-in Node tests for pure UI logic and a fake DOM, not browser/Quest QA. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {normalize, readBounded, start} = require('../dashboard/telemetry.js');
const sample = () => ({schema:1,mock:true,age:0,mode:'SIM',battery:50,deadman:false,acks:[]});
test('shared Python/JS semantic corpus agrees on expected status', () => {
  const fixtures=require('../tests/fixtures/telemetry_contract.json');
  for(const fixture of fixtures) {
    assert.equal(normalize(fixture.payload,fixture.elapsed).status,fixture.browser_status,fixture.name);
  }
});

test('boolean numeric impostors invalidate the entire view', () => {
  for (const key of ['age','battery']) {
    const data=sample(); data[key]=true;
    assert.equal(normalize(data,0).status,'INVALID');
  }
});
test('unknown fields and exact booleans are enforced', () => {
  for (const data of [{...sample(),extra:1},{...sample(),mock:1},{...sample(),deadman:'false'}]) {
    assert.equal(normalize(data,0).status,'INVALID');
  }
});
test('source age and entire request duration are conservative', () => {
  assert.equal(normalize({...sample(),age:1},1).status,'STALE');
  assert.equal(normalize({...sample(),age:1},.99).status,'MOCK DATA');
});
test('mode is bounded in code points and controls are rejected', () => {
  assert.equal(normalize({...sample(),mode:'🚁'.repeat(64)},0).status,'MOCK DATA');
  assert.equal(normalize({...sample(),mode:'🚁'.repeat(65)},0).status,'INVALID');
  assert.equal(normalize({...sample(),mode:'SIM\nACTIVE'},0).status,'INVALID');
});
test('history count and text limits reject instead of silently truncating', () => {
  assert.equal(normalize({...sample(),acks:Array(31).fill('x')},0).status,'INVALID');
  assert.equal(normalize({...sample(),acks:['x'.repeat(257)]},0).status,'INVALID');
});
test('Unicode direction controls and unpaired surrogates are invalid labels', () => {
  for(const mode of ['SAFE\u202e','\ud800','SIM\u0085']) {
    assert.equal(normalize({...sample(),mode},0).status,'INVALID');
  }
  assert.equal(normalize({...sample(),mode:'СИМ / SIM 🚁'},0).status,'MOCK DATA');
});
test('invalid timing and configuration do not look healthy', () => {
  for (const elapsed of [-1,NaN,Infinity]) assert.equal(normalize(sample(),elapsed).status,'INVALID');
  assert.throws(() => normalize(sample(),0,0));
});
test('history snapshot does not alias its input', () => {
  const data=sample(); data.acks.push('one');
  const view=normalize(data,0); data.acks.push('two');
  assert.deepEqual(view.acks,['one']);
});
test('bounded reader handles split UTF-8 and rejects oversize bodies', async () => {
  const encoded=new TextEncoder().encode(JSON.stringify({...sample(),mode:'СИМ'}));
  const stream=new ReadableStream({start(c){for(const byte of encoded)c.enqueue(Uint8Array.of(byte));c.close();}});
  assert.equal((await readBounded(new Response(stream))).mode,'СИМ');
  await assert.rejects(readBounded(new Response('x'.repeat(100)),10));
});
test('bad encoding, null bodies and malformed JSON reject', async () => {
  await assert.rejects(readBounded(new Response(Uint8Array.of(255))));
  await assert.rejects(readBounded(new Response(null)));
  await assert.rejects(readBounded(new Response('{')));
});

function dom() {
  const nodes={};
  for(const id of ['link','mode','battery','deadman','telemetry-note','history-note','acks']) {
    nodes[id]={textContent:'previous',children:[],replaceChildren(){this.children=[];},append(row){this.children.push(row);}};
  }
  const listeners={};
  return {nodes,listeners,hidden:false,getElementById:id=>nodes[id] || null,
    createElement:()=>({textContent:''}),addEventListener:(type,fn)=>{listeners[type]=fn;}};
}
test('mock success renders text and schedules one expiry plus one next poll', async () => {
  const document=dom(), calls=[];
  const data={...sample(),acks:['<img src=x onerror=alert(1)>']};
  await start(document,async()=>new Response(JSON.stringify(data)),()=>0,(fn,delay)=>calls.push({fn,delay}));
  assert.equal(document.nodes.link.textContent,'MOCK DATA');
  assert.equal(document.nodes.acks.children[0].textContent,data.acks[0]);
  assert.equal(calls.length,2); assert.equal(calls[0].delay,2000); assert.equal(calls[1].delay,1000);
  assert.equal(document.nodes.deadman.textContent,'REPORTED RELEASED');
});
test('failed poll clears values and marks retained history stale', async () => {
  const document=dom(); document.nodes.acks.children.push({textContent:'old'});
  await start(document,async()=>{throw Error('offline');},()=>0,()=>{});
  for(const id of ['mode','battery','deadman']) assert.equal(document.nodes[id].textContent,'unknown');
  assert.match(document.nodes['history-note'].textContent,/stale/);
  assert.equal(document.nodes.acks.children.length,1);
});
test('slow successful response is stale even when source claims zero age', async () => {
  const document=dom(); let clock=0;
  await start(document,async()=>{clock=2000;return new Response(JSON.stringify(sample()));},()=>clock,()=>{});
  assert.equal(document.nodes.link.textContent,'STALE');
  assert.equal(document.nodes.battery.textContent,'unknown');
});
test('expiry clears health even while next request could still be pending', async () => {
  const document=dom(),calls=[];
  await start(document,async()=>new Response(JSON.stringify(sample())),()=>0,(fn,delay)=>calls.push({fn,delay}));
  calls.find(call=>call.delay===2000).fn();
  assert.equal(document.nodes.link.textContent,'STALE');
  assert.equal(document.nodes.battery.textContent,'unknown');
});
test('an earlier expiry cannot overwrite a newer accepted sample', async () => {
  const document=dom(),calls=[];
  await start(document,async()=>new Response(JSON.stringify(sample())),()=>0,(fn,delay)=>calls.push({fn,delay}));
  const oldExpiry=calls[0].fn;
  await calls[1].fn();
  oldExpiry();
  assert.equal(document.nodes.link.textContent,'MOCK DATA');
});
test('visibility change invalidates displayed values and an in-flight response', async () => {
  const document=dom();
  await start(document,async()=>{
    document.listeners.visibilitychange();
    return new Response(JSON.stringify(sample()));
  },()=>0,()=>{});
  assert.equal(document.nodes.mode.textContent,'unknown');
  assert.equal(document.nodes.link.textContent,'OFFLINE / VISIBILITY CHANGED');
});
test('hidden document makes no telemetry request', async () => {
  const document=dom();document.hidden=true;let count=0;
  await start(document,async()=>{count++;},()=>0,()=>{});
  assert.equal(count,0);
  assert.equal(document.nodes.link.textContent,'OFFLINE / HIDDEN');
});
