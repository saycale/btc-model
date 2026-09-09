/* Shared, dependency-free math and state helpers for both language pages.
   The page-specific layer owns rendering; this file owns reproducible mechanics. */
(function(global){
  'use strict';
  function regress(xs,ys){
    const n=xs.length;if(n<3)return null;
    let mx=0,my=0;for(let i=0;i<n;i++){mx+=xs[i];my+=ys[i];}mx/=n;my/=n;
    let sxx=0,syy=0,sxy=0;
    for(let i=0;i<n;i++){const dx=xs[i]-mx,dy=ys[i]-my;sxx+=dx*dx;syy+=dy*dy;sxy+=dx*dy;}
    if(!sxx||!syy)return null;
    const b=sxy/sxx,a=my-b*mx,u=[];let sse=0;
    for(let i=0;i<n;i++){const e=ys[i]-a-b*xs[i];u.push(e);sse+=e*e;}
    const sx=xs.reduce((s,v)=>s+v,0),sx2=xs.reduce((s,v)=>s+v*v,0),det=n*sx2-sx*sx;
    const inv=[[sx2/det,-sx/det],[-sx/det,n/det]],M=[[0,0],[0,0]],L=Math.min(12,n-1);
    const add=(i,j,w)=>{const xi=[1,xs[i]],xj=[1,xs[j]],v=w*u[i]*u[j];
      for(let r=0;r<2;r++)for(let c=0;c<2;c++)M[r][c]+=v*(xi[r]*xj[c]+(i===j?0:xj[r]*xi[c]));};
    for(let i=0;i<n;i++)add(i,i,1);
    for(let lag=1;lag<=L;lag++){const w=1-lag/(L+1);for(let i=lag;i<n;i++)add(i,i-lag,w);}
    const V=[[0,0],[0,0]];
    for(let r=0;r<2;r++)for(let c=0;c<2;c++)for(let j=0;j<2;j++)for(let k=0;k<2;k++)V[r][c]+=inv[r][j]*M[j][k]*inv[k][c];
    return{a,b,r2:1-sse/syy,se:Math.sqrt(sse/(n-2)/sxx),hac:Math.sqrt(Math.max(V[1][1],0)),n};
  }
  function priceFit(observations,start,lastDate,gen){
    const x=[],y=[];
    for(let j=0;j<observations.length;j++){
      const n=start[0]*12+start[1]+j,mm=[Math.floor((n-1)/12),(n-1)%12+1];
      const t=j===observations.length-1?Date.UTC(...[lastDate[0],lastDate[1]-1,lastDate[2]]):Date.UTC(mm[0],mm[1],0);
      x.push(Math.log10((t-gen)/864e5));y.push(Math.log10(observations[j]));
    }
    const r=regress(x,y),mx=x.reduce((s,v)=>s+v,0)/x.length,my=y.reduce((s,v)=>s+v,0)/y.length;
    return{q:r.b,beta:r.b/3,tPivot:10**mx,logPPivot:my,r2:r.r2,hac:r.hac};
  }
  function readScenario(defaults){
    const q=new URLSearchParams(location.search),out={...defaults};
    // Missing/empty URL values are not zero: retain the calibrated baseline.
    const bounds={k:[700,3200],de:[0,1],dp:[0,1],b:[1.6,2.05]};
    for(const k of Object.keys(defaults)){
      const raw=q.get(k);
      if(raw===null||raw.trim()==='')continue;
      const v=Number(raw),range=bounds[k];
      if(Number.isFinite(v)&&(!range||(v>=range[0]&&v<=range[1])))out[k]=v;
    }
    return out;
  }
  function scenarioURL(state){
    const u=new URL(location.href);for(const[k,v]of Object.entries(state))u.searchParams.set(k,v);return u.toString();
  }
  function replaceScenarioURL(state){history.replaceState(null,'',scenarioURL(state));}
  global.BTCModelCore={regress,priceFit,readScenario,scenarioURL,replaceScenarioURL};
})(window);
