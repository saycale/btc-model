'use strict';
const assert=require('node:assert/strict');
global.window=global;
global.location={search:''};
require('../model-core.js');
const {residualMetrics,readScenario}=BTCModelCore;
const residuals=[null,0,-0.1,0.2,-0.3,0.5,NaN,undefined,Infinity];
const strict=residualMetrics(residuals,0.1);
assert.equal(strict.n,5);
assert.equal(strict.bad,3); // exactly on the boundary is inside
assert.ok(Math.abs(strict.mae-0.22)<1e-12);
assert.ok(Math.abs(strict.rmse-Math.sqrt(0.39/5))<1e-12);
for(const band of [0.1,0.2,0.3,0.5]){
  const m=residualMetrics(residuals,band);
  assert.equal(m.mae,strict.mae);
  assert.equal(m.rmse,strict.rmse);
  assert.ok(m.bad<=strict.bad);
  location.search='?band='+band;
  assert.equal(readScenario({band:0.2}).band,band);
}
for(const query of ['', '?band=', '?band=no', '?band=0', '?band=0.25', '?band=Infinity']){
  location.search=query;
  assert.equal(readScenario({band:0.2}).band,0.2);
}
assert.deepEqual(residualMetrics([null,NaN],0.2),{n:0,bad:0,mae:null,rmse:null});
assert.throws(()=>residualMetrics([0],0),RangeError);
// Subtract the cycle component in log space: a perfectly matched cycle
// must leave zero error for the full model, despite trend deviations.
const cycle=[0.3,-0.4,0.1];
assert.equal(residualMetrics(cycle,0.2).bad,2);
assert.equal(residualMetrics(cycle.map((r,i)=>r-cycle[i]),0.2).rmse,0);
console.log('ok: residual counts, boundary, MAE/RMSE, cycle subtraction and diagnostic URL state');
