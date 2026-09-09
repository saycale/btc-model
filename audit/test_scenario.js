/* Executable state tests: no browser, network, or third-party dependencies. */
'use strict';
const assert = require('node:assert/strict');
global.window = global;
global.location = {href:'https://example.test/btc-model/ru.html',search:''};
require('../model-core.js');
const defaults = {k:1610,de:0.15,dp:0.5,b:1.897};
function read(search) {
  location.search = search;
  return BTCModelCore.readScenario(defaults);
}
assert.deepEqual(read(''), defaults);
assert.deepEqual(read('?build=123'), defaults);
assert.deepEqual(read('?k=&de=%20&dp=&b='), defaults);
assert.deepEqual(read('?k=2000'), {...defaults,k:2000});
assert.deepEqual(read('?de=0&dp=0'), {...defaults,de:0,dp:0});
assert.deepEqual(read('?k=700&de=1&dp=1&b=2.05'), {k:700,de:1,dp:1,b:2.05});
assert.deepEqual(read('?k=3200&de=0&dp=0&b=1.6'), {k:3200,de:0,dp:0,b:1.6});
assert.deepEqual(read('?k=NaN&de=Infinity&dp=bad&b=-Infinity'), defaults);
assert.deepEqual(read('?k=0&de=-0.1&dp=1.1&b=100'), defaults);
assert.deepEqual(read('?k=3201&de=2&dp=-1&b=1.59'), defaults);
assert.deepEqual(read('?unknown=5&de=0.25'), {...defaults,de:0.25});
assert.deepEqual(defaults, {k:1610,de:0.15,dp:0.5,b:1.897});
// Sharing and restoring preserve the numeric scenario, unrelated query and anchor.
location.href = 'https://example.test/btc-model/ru.html?build=123#model';
const state = {k:2100,de:0.35,dp:0.8,b:1.95};
const shared = new URL(BTCModelCore.scenarioURL(state));
assert.equal(shared.searchParams.get('build'), '123');
assert.equal(shared.hash, '#model');
assert.deepEqual(read(shared.search), state);
let replaced;
global.history = {replaceState(data,title,url){replaced=url;}};
BTCModelCore.replaceScenarioURL(state);
assert.equal(replaced, shared.toString());
console.log('ok: default, partial, zero, bounds, invalid and round-trip scenario tests');
