'use strict';
const $ = (id) => document.getElementById(id);
const state = { source: 'demo', offers: [], result: null, selected: null, lastRequest: null, tools: [], raw: null, rawTool: null, editing: null, draftSource: 'manual' };
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const yuan = (n) => n == null ? '待确认' : (n / 100).toFixed(2);
const clock = (s) => s.slice(11,16);
const localValue = (s) => s.slice(0,16);
const chinaNow = () => new Date(Date.now() + 8 * 3600000).toISOString().slice(0,16);
const shiftMinutes = (iso, minutes) => new Date(new Date(iso + '+08:00').getTime() + minutes * 60000 + 8 * 3600000).toISOString().slice(0,16);
let toastTimer, calculationVersion=0;
function toast(message) { $('toast').textContent=message; $('toast').hidden=false; clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('toast').hidden=true, 6500); }
async function api(path, data, asBlob=false) {
  const response = await fetch(path, data ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)} : {});
  if (!response.ok) { const body = await response.json().catch(()=>({})); throw new Error(body.error || '本机服务暂时不可用'); }
  return asBlob ? response.blob() : response.json();
}
function view(name) {
  for(const section of document.querySelectorAll('.view')) section.hidden = section.id !== 'view-' + name;
  for(const nav of document.querySelectorAll('.nav')) nav.classList.toggle('active',nav.dataset.view===name);
  $('page-name').textContent={planner:'空档规划',offers:'优惠候选',connection:'MCP 连接'}[name];
  window.scrollTo({top:0,behavior:'instant'});
}
function mode() {
  const names={demo:'演示数据',manual:'手动录入',mcp:'MCP 候选'};
  $('mode-label').textContent='◉ '+names[state.source];
  const messages={demo:'用示例优惠体验空档规划，出发时间可自行调整。',manual:'填写常用优惠，安排自己的饭点。',mcp:'已导入 MCP 查询结果，可在优惠候选中查看详情。'};
  $('notice').innerHTML='<span>'+names[state.source]+'</span> '+messages[state.source]+(state.source==='demo'?'<button id="real-mode">使用我的数据 ↗</button>':'');
  $('offer-count').textContent=state.offers.length;
  if(state.tools.length) $('connection-status').textContent='已连接，发现 '+state.tools.length+' 个可用查询工具。'+(state.source==='mcp'?'已建立 '+state.offers.length+' 个 MCP 候选；未核对的候选不会直接推荐。':'查询结果尚未作为 MCP 候选导入。');
}
function fillForm(data) {
  $('now').value=localValue(data.now); $('free-until').value=localValue(data.free_until);
  $('budget').value=yuan(data.budget_fen);
  for(const [id,key] of [['travel','travel_minutes'],['queue','queue_minutes'],['meal','meal_minutes'],['buffer','buffer_minutes']]) $(id).value=data[key];
  $('strategy').value=data.strategy||'budget';
}
function requestData() {
  if (!$('plan-form').reportValidity()) throw new Error('请先填好空档参数');
  return {source:state.source,now:$('now').value+'+08:00',free_until:$('free-until').value+'+08:00',budget_fen:Math.round(Number($('budget').value)*100),
    travel_minutes:Number($('travel').value),queue_minutes:Number($('queue').value),meal_minutes:Number($('meal').value),buffer_minutes:Number($('buffer').value),strategy:$('strategy').value,offers:state.offers};
}
async function calculate() {
  const version=++calculationVersion;
  $('calculate').disabled=true;
  try {
    const data=JSON.parse(JSON.stringify(requestData()));
    const result=await api('/api/plan',data);
    if(version!==calculationVersion)return;
    state.result=result; state.lastRequest=data;
    if(!result.feasible.some(x=>x.id===state.selected)) state.selected=result.recommendation?.id||null;
    renderResult();
  } catch(error) {
    if(version!==calculationVersion)return;
    state.result=null;state.lastRequest=null;state.selected=null;
    $('result-count').textContent='参数未通过检查';
    $('result').innerHTML='<div class="empty-state"><h3>先把空档参数填好。</h3><p>'+esc(error.message)+'</p></div>';
    $('alternatives').innerHTML='';$('excluded').innerHTML='';$('excluded-count').textContent='0';
    toast(error.message);
  }
  finally { if(version===calculationVersion)$('calculate').disabled=false; }
}
function renderResult() {
  const r=state.result;
  $('hero-minutes').textContent=r.available_minutes;
  $('hero-time').textContent=clock(r.now)+' — '+clock(r.free_until);
  $('result-count').textContent=r.feasible.length+' 个可行 / '+(r.feasible.length+r.excluded.length)+' 个候选';
  const item=r.feasible.find(x=>x.id===state.selected)||r.recommendation;
  if(item) {
    const points=[['出发',item.depart_at],['到店',item.arrive_at],['点单',item.order_at],['用餐结束',item.finish_at],['返回',item.return_at]];
    $('result').innerHTML=`<article class="recommendation"><div class="recommend-top"><span class="tag">${item.id===r.recommendation?.id?'优先推荐':'已选方案'}</span><span class="recommend-meta">返回后距下次安排 ${item.spare_minutes} 分钟</span></div><div class="recommend-body"><div><h3>${esc(item.name)}</h3><p>预算余量 ¥${yuan(item.unspent_fen)} · 到店至点单预留 ${item.wait_minutes} 分钟</p></div><div class="price"><small>¥</small>${yuan(item.price_fen)}</div></div><div class="timeline">${points.map(([label,time])=>`<div><strong>${clock(time)}</strong>${label}</div>`).join('')}</div><div class="recommend-foot"><span>已另留 ${r.buffer_minutes} 分钟缓冲，${clock(item.buffer_until)} 前完成安排。</span><div class="download-actions"><button class="button outline" data-download="calendar">导出日历 ↗</button><button class="button outline" data-download="report">保存安排 ↓</button></div></div></article>`;
    const alternatives=r.feasible.filter(x=>x.id!==item.id);
    $('alternatives').innerHTML=alternatives.length?`<div class="alternatives">${alternatives.map(x=>`<article class="alternative"><div><strong>${esc(x.name)}</strong><small>${clock(x.return_at)} 返回 · 余 ${x.spare_minutes} 分钟</small></div><span class="alt-price">¥${yuan(x.price_fen)}</span><button class="alt-select" data-select="${esc(x.id)}" aria-label="选择${esc(x.name)}">↗</button></article>`).join('')}</div>`:'';
  } else {
    $('result').innerHTML=`<div class="empty-state"><div class="empty-icon">◷</div><h3>这次，先不赶这一顿。</h3><p>${esc(r.message)}<br>按当前设置，往返、排队、用餐和缓冲至少需要 ${r.required_minutes} 分钟。</p><button class="button outline" data-view="offers">检查优惠候选 ↗</button></div>`;
    $('alternatives').innerHTML='';
  }
  $('excluded-count').textContent=r.excluded.length;
  $('excluded').innerHTML=r.excluded.length?r.excluded.map(x=>`<div class="excluded-row"><strong>${esc(x.name)}</strong><span>${x.reasons.map(esc).join('；')}</span></div>`).join(''):'<p>所有候选均已通过本次条件检查。</p>';
}
function renderOffers() {
  mode();
  $('offers-list').innerHTML=state.offers.length?state.offers.map(x=>`<article class="offer-row"><div class="offer-data"><strong>${esc(x.name)}</strong><span class="verification ${!x.verified?'pending':''}">${state.source==='demo'?'演示':x.verified?'已核对':'待核对'}</span><p>有效至 ${esc(x.valid_to.slice(0,16).replace('T',' '))} ${x.daily_windows?.length?'· 每日 '+x.daily_windows.map(w=>w.map(esc).join('—')).join(' / '):''}</p><p>${esc(x.note||'未填写附加条件')}</p></div><span class="offer-price">${x.price_fen==null?'待定价':'¥'+yuan(x.price_fen)}</span><div class="row-actions"><button data-edit="${esc(x.id)}">编辑</button><button class="delete" data-remove="${esc(x.id)}">移除</button></div></article>`).join(''):'<div class="empty-state"><h3>给你的空档，放进第一个选择。</h3><p>可手动录入已核对的优惠，或前往 MCP 连接查询。</p><button class="button outline" data-view="connection">连接 MCP ↗</button></div>';
}
async function loadDemo() {
  try { const data=await api('/api/demo'); state.source='demo'; state.offers=data.offers; state.selected=null; fillForm(data); renderOffers(); await calculate(); }
  catch(error){toast('加载演示失败：'+error.message);}
}
async function manualMode() {
  state.source='manual';state.offers=[];state.selected=null;
  $('now').value=chinaNow();$('free-until').value=shiftMinutes($('now').value,90);
  renderOffers(); await calculate(); view('offers');
  toast('已切换到你的数据，演示优惠已清空。');
}
function openOffer(id=null,fromMcp=false) {
  const offer=state.offers.find(x=>x.id===id);
  state.editing=offer?.id||null;state.draftSource=fromMcp?'mcp':state.source;
  $('offer-form').reset();$('offer-error').textContent='';
  const now=$('now').value||chinaNow();
  $('offer-dialog-title').textContent=offer?'编辑优惠候选':'添加优惠候选';
  $('offer-source-hint').textContent=fromMcp?'填写优惠信息；保存后替换当前候选。':state.source==='demo'?'编辑示例优惠。':'补充价格、时段和适用条件。';
  $('offer-name').value=offer?.name||'';$('offer-price').value=offer?.price_fen==null?'':yuan(offer.price_fen);
  $('offer-note').value=offer?.note||'';
  $('offer-start').value=offer?localValue(offer.valid_from):now;
  $('offer-end').value=offer?localValue(offer.valid_to):now.slice(0,10)+'T23:59';
  $('offer-window-start').value=offer?.daily_windows?.[0]?.[0]||'';
  $('offer-window-end').value=offer?.daily_windows?.[0]?.[1]||'';
  $('offer-evidence').value=offer?.evidence||'';
  $('offer-evidence').placeholder=fromMcp?'摘录 '+state.rawTool+' 中的相关优惠信息':'相关查询原文或你核对的信息';
  $('offer-verified').checked=offer?.verified||false;
  $('offer-dialog').showModal();
}
async function saveOffer(event) {
  event.preventDefault();
  const a=$('offer-window-start').value,b=$('offer-window-end').value;
  if(Boolean(a)!==Boolean(b)) { $('offer-error').textContent='每日可用开始与结束时间需要一起填写。';return; }
  if($('offer-end').value<=$('offer-start').value) { $('offer-error').textContent='有效期结束必须晚于开始。';return; }
  if(state.draftSource==='mcp'&&!$('offer-evidence').value.trim()) { $('offer-error').textContent='MCP 候选需要保留相关原文依据。';return; }
  const offer={id:state.editing||crypto.randomUUID(),name:$('offer-name').value.trim(),price_fen:$('offer-price').value===''?null:Math.round(Number($('offer-price').value)*100),valid_from:$('offer-start').value+'+08:00',valid_to:$('offer-end').value+'+08:00',daily_windows:a?[[a,b]]:[],note:$('offer-note').value.trim(),evidence:$('offer-evidence').value.trim(),verified:$('offer-verified').checked};
  if(state.draftSource!==state.source){state.source=state.draftSource;state.offers=[];state.selected=null;}
  const index=state.offers.findIndex(x=>x.id===offer.id);
  if(index>=0) state.offers[index]=offer;else state.offers.push(offer);
  $('offer-dialog').close();renderOffers();await calculate();toast('已保存，空档规划已更新。');
}
async function download(kind) {
  try {
    if(!state.lastRequest)throw new Error('请先完成一次有效规划');
    const data={...state.lastRequest,selected_id:state.selected};
    const blob=await api('/api/'+kind,data,true),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=kind==='calendar'?'mcwindow.ics':'mcwindow-plan.md';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);toast(kind==='calendar'?'日历已导出，可用系统日历打开。':'安排已保存为 Markdown。');
  }catch(error){toast(error.message);}
}
function toolDetails() {
  const tool=state.tools.find(x=>x.name===$('tool-name').value);
  $('tool-description').textContent=tool?.description||'';
  $('tool-schema').textContent=JSON.stringify(tool?.inputSchema||{},null,2);
  $('tool-arguments').value='{}';$('raw-section').hidden=true;
}
async function connect() {
  $('connect').disabled=true;$('connection-status').classList.remove('error');$('connection-status').textContent='正在连接官方服务…';
  try {
    const data=await api('/api/mcp/tools',{token:$('token').value});state.tools=data.tools;
    if(!state.tools.length)throw new Error('连接成功，但服务器未提供本项目所用的查询工具。');
    $('tool-name').innerHTML=state.tools.map(t=>`<option value="${esc(t.name)}">${esc(t.name)}</option>`).join('');
    $('tool-workspace').hidden=false;toolDetails();
    mode();
  }catch(error){state.tools=[];$('tool-workspace').hidden=true;$('connection-status').classList.add('error');$('connection-status').textContent=error.message;}
  finally{$('connect').disabled=false;}
}
async function callTool() {
  $('call-tool').disabled=true;
  try{
    let args;try{args=JSON.parse($('tool-arguments').value);}catch{throw new Error('调用参数不是有效 JSON');}
    if(!args||typeof args!=='object'||Array.isArray(args))throw new Error('调用参数须为 JSON 对象');
    const data=await api('/api/mcp/call',{token:$('token').value,name:$('tool-name').value,arguments:args});
    state.raw=data.result;state.rawTool=data.tool;$('raw-result').textContent=JSON.stringify(data.result,null,2);$('raw-section').hidden=false;
    $('offer-from-mcp').hidden=data.tool==='now-time-info';toast('查询完成，可以建立候选了。');
  }catch(error){toast(error.message);}
  finally{$('call-tool').disabled=false;}
}
document.addEventListener('click',async event=>{
  const target=event.target.closest('button');if(!target)return;
  if(target.dataset.view)view(target.dataset.view);
  if(target.dataset.select){state.selected=target.dataset.select;renderResult();}
  if(target.dataset.download)await download(target.dataset.download);
  if(target.dataset.edit)openOffer(target.dataset.edit);
  if(target.dataset.remove){state.offers=state.offers.filter(x=>x.id!==target.dataset.remove);renderOffers();await calculate();}
  if(target.id==='real-mode')await manualMode();
});
$('plan-form').addEventListener('submit',e=>{e.preventDefault();state.selected=null;calculate();});
$('plan-form').addEventListener('change',()=>{state.selected=null;calculate();});
$('offer-form').addEventListener('submit',saveOffer);
$('new-offer').addEventListener('click',()=>openOffer());
$('close-dialog').addEventListener('click',()=>$('offer-dialog').close());
$('cancel-dialog').addEventListener('click',()=>$('offer-dialog').close());
$('offer-from-mcp').addEventListener('click',()=>openOffer(null,true));
$('back-plan').addEventListener('click',()=>view('planner'));
$('mode-label').addEventListener('click',()=>view('connection'));
$('reload-demo').addEventListener('click',async()=>{await loadDemo();view('planner');toast('演示已重置。');});
$('current-time').addEventListener('click',()=>{$('now').value=chinaNow();$('free-until').value=shiftMinutes($('now').value,90);calculate();});
$('connect').addEventListener('click',connect);
$('call-tool').addEventListener('click',callTool);
$('tool-name').addEventListener('change',toolDetails);
$('forget-token').addEventListener('click',()=>{$('token').value='';state.raw=null;state.rawTool=null;state.tools=[];$('tool-workspace').hidden=true;$('raw-result').textContent='';$('connection-status').textContent='Token 和查询原文已从当前页面清除。';$('connection-status').classList.remove('error');toast('已清除连接凭证。');});
loadDemo();
