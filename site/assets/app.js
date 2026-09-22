import {readContract,readGlobalConstitution,submitAndFinalize} from './genlayer-client.js';

const CONTRACT_ADDRESS='0x02E5Ac4D8E718e15EdF6c52C48908d45a1A628bB';
const STUDIONET_CHAIN_ID=61999;
const STUDIONET_CHAIN_HEX='0xF22F';
const STUDIONET_RPC='https://studio.genlayer.com/api';
const EXPLORER='https://explorer-studio.genlayer.com';
const PUBLIC_RECORD={protocolId:'proofhalt-studionet-demo',incidentId:'PH-000001'};

const protocolStatuses=['NONE','INTEGRATION PENDING','PROTECTED','DEACTIVATION PENDING','INACTIVE'];
const incidentStatuses=['NONE','OPEN','DISMISSED','WATCH','HALT AUTHORIZED','HALTED','REVIEW DUE','REMEDIATION SUBMITTED','KEEP HALTED','RESTORE AUTHORIZED','RESTORED','CLOSED'];
const actionNames=['NONE','MONITOR','HALT','KEEP HALTED','RESTORE'];
let connectedAddress='';

const $=id=>document.getElementById(id);
const navWalletBtn=$('navWalletBtn');
const navWalletLabel=$('navWalletLabel');
const walletBtn=$('walletBtn');
const verifyContractBtn=$('verifyContractBtn');
const walletStatus=$('walletStatus');
const networkStatus=$('networkStatus');
const contractStatus=$('contractStatus');
const constitutionStatus=$('constitutionStatus');
const walletMessage=$('walletMessage');
const txLog=$('txLog');
const readResult=$('readResult');

function shortAddress(value){return value?`${value.slice(0,6)}…${value.slice(-4)}`:'—'}
function normalize(value){
  if(typeof value==='string'){try{return JSON.parse(value)}catch{return value}}
  return value;
}
function safeJson(value){return JSON.stringify(value,(_,item)=>typeof item==='bigint'?item.toString():item,2)}
function errorMessage(error){
  const message=error instanceof Error?error.message:String(error||'Unknown error');
  if(Number(error?.code)===4001||/rejected|denied/i.test(message))return 'Wallet request cancelled. Nothing was submitted.';
  return message.replace(/^Error:\s*/,'').slice(0,700);
}
function setMessage(message,tone='muted'){walletMessage.textContent=message;walletMessage.dataset.tone=tone}
function explorerTx(hash){return `${EXPLORER}/tx/${hash}`}
function addLog(state,title,detail='',hash=''){
  txLog.querySelector('.empty')?.remove();
  const li=document.createElement('li');li.dataset.state=state;
  const strong=document.createElement('strong');strong.textContent=title;li.append(strong);
  if(detail){const span=document.createElement('span');span.textContent=detail;li.append(span)}
  if(hash){const a=document.createElement('a');a.href=explorerTx(hash);a.target='_blank';a.rel='noreferrer';a.textContent=`${shortAddress(hash)} · open transaction ↗`;li.append(a)}
  txLog.prepend(li);
}
function showRead(label,value){readResult.textContent=`${label}\n${safeJson(normalize(value))}`}

async function ensureStudionet(provider){
  const current=await provider.request({method:'eth_chainId'});
  if(parseInt(current,16)===STUDIONET_CHAIN_ID)return;
  try{await provider.request({method:'wallet_switchEthereumChain',params:[{chainId:STUDIONET_CHAIN_HEX}]})}
  catch(error){
    if(Number(error?.code)!==4902)throw error;
    await provider.request({method:'wallet_addEthereumChain',params:[{chainId:STUDIONET_CHAIN_HEX,chainName:'GenLayer Studionet',nativeCurrency:{name:'GEN',symbol:'GEN',decimals:18},rpcUrls:[STUDIONET_RPC],blockExplorerUrls:[EXPLORER]}]});
    await provider.request({method:'wallet_switchEthereumChain',params:[{chainId:STUDIONET_CHAIN_HEX}]});
  }
}
async function refreshNetwork(){
  if(!window.ethereum)return;
  try{const id=parseInt(await window.ethereum.request({method:'eth_chainId'}),16);networkStatus.textContent=id===STUDIONET_CHAIN_ID?'Studionet · chain 61999':`Wrong network · chain ${id}`;networkStatus.classList.toggle('ok',id===STUDIONET_CHAIN_ID)}
  catch{networkStatus.textContent='Network unavailable'}
}
async function connectWallet(){
  if(!window.ethereum){setMessage('MetaMask was not detected. Install it only from metamask.io, then return to this page.','error');return}
  walletBtn.disabled=true;navWalletBtn.disabled=true;walletStatus.textContent='Waiting for MetaMask…';setMessage('Approve account access and the Studionet network switch in MetaMask. No transaction is sent by connecting.');
  try{
    const accounts=await window.ethereum.request({method:'eth_requestAccounts'});
    if(!accounts?.[0])throw new Error('No account selected');
    connectedAddress=accounts[0];await ensureStudionet(window.ethereum);await refreshNetwork();
    walletStatus.textContent=shortAddress(connectedAddress);walletStatus.classList.add('ok');navWalletLabel.textContent=shortAddress(connectedAddress);navWalletBtn.classList.add('connected');walletBtn.textContent='Wallet connected';walletBtn.classList.add('connected');
    setMessage('Connected. ProofHalt will request a zero-value transaction only after you click a named write action.','success');
  }catch(error){connectedAddress='';walletStatus.textContent='Not connected';walletStatus.classList.remove('ok');setMessage(errorMessage(error),'error')}
  finally{walletBtn.disabled=false;navWalletBtn.disabled=false}
}
function disconnectUi(){connectedAddress='';walletStatus.textContent='Not connected';walletStatus.classList.remove('ok');navWalletLabel.textContent='Connect MetaMask';navWalletBtn.classList.remove('connected');walletBtn.textContent='Connect MetaMask';walletBtn.classList.remove('connected');setMessage('Wallet disconnected. Public reads remain available.')}

async function verifyLiveContract(){
  verifyContractBtn.disabled=true;contractStatus.textContent='Reading finalized state…';constitutionStatus.textContent='Loading…';
  try{
    const data=normalize(await readGlobalConstitution(CONTRACT_ADDRESS));
    if(!data||typeof data!=='object')throw new Error('Unexpected contract response');
    contractStatus.textContent=`Verified · ${shortAddress(CONTRACT_ADDRESS)}`;contractStatus.classList.add('ok');
    constitutionStatus.textContent=`${data.enforcement_mode||data.schema} · ${data.minimum_independent_groups} origins`;constitutionStatus.classList.add('ok');
    setMessage(`Live ${data.schema} state verified. External enforcement supported: ${data.external_enforcement_supported===true?'yes':'no (authorization record only)'}.`,'success');
    $('liveContractMetric').textContent=String(data.schema||'LIVE').toUpperCase();
    return data;
  }catch(error){contractStatus.textContent='Verification failed';contractStatus.classList.remove('ok');constitutionStatus.textContent='Unavailable';constitutionStatus.classList.remove('ok');setMessage(`Live read failed: ${errorMessage(error)}`,'error');throw error}
  finally{verifyContractBtn.disabled=false}
}

function canonicalize(value){
  if(Array.isArray(value))return `[${value.map(canonicalize).join(',')}]`;
  if(value&&typeof value==='object')return `{${Object.keys(value).sort().map(key=>`${JSON.stringify(key)}:${canonicalize(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
async function sha256(text){const bytes=new TextEncoder().encode(text);const hash=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,'0')).join('')}
async function constitutionPayload(text){const canonical=canonicalize(JSON.parse(text));return {canonical,hash:await sha256(canonical)}}
function assertSourceSnapshotBinding(sourceValue,snapshotValue){
  const source=sourceValue.trim();const snapshot=snapshotValue.trim();
  if(source===snapshot)return 'DIRECT_SOURCE_BYTES';
  const sourceUrl=new URL(source);const snapshotUrl=new URL(snapshot);
  const sourceParts=sourceUrl.pathname.replace(/^\/+|\/+$/g,'').split('/');
  const snapshotParts=snapshotUrl.pathname.replace(/^\/+|\/+$/g,'').split('/');
  const githubCommitRaw=sourceUrl.hostname.toLowerCase()==='github.com'
    && snapshotUrl.hostname.toLowerCase()==='raw.githubusercontent.com'
    && sourceParts.length>=5 && snapshotParts.length>=4
    && sourceParts[2]==='blob' && /^[0-9a-f]{40}$/i.test(sourceParts[3])
    && sourceParts[0].toLowerCase()===snapshotParts[0].toLowerCase()
    && sourceParts[1].toLowerCase()===snapshotParts[1].toLowerCase()
    && sourceParts[3].toLowerCase()===snapshotParts[2].toLowerCase()
    && sourceParts.slice(4).join('/')===snapshotParts.slice(3).join('/');
  if(githubCommitRaw)return 'GITHUB_COMMIT_RAW';
  throw new Error('Source/snapshot mismatch: use the exact same URL, or matching GitHub blob/raw URLs pinned to one 40-character commit.');
}
async function generateConstitution(){
  const target=$('targetInput').value.trim();const protocolId=document.querySelector('#registerForm [name=protocolId]').value.trim();
  if(!/^0x[0-9a-fA-F]{40}$/.test(target)){setMessage('Enter the target contract address before generating the constitution.','error');return}
  const constitution={schema:'proofhalt-protocol-constitution/v2',protocol_id:protocolId,protected_targets:[target],dependencies:[],halt_conditions:[{id:'ACTIVE_UNAUTHORIZED_WITHDRAWAL',description:'A presently active unauthorized withdrawal or equivalent critical state transition affecting the registered target.'}],exclusions:['Historical incidents with no active exploit','Price volatility or governance disagreement without technical exploitation','Unverified, hash-mismatched or source/snapshot-mismatched evidence'],minimum_independent_groups:2,requires_technical_anchor:true,critical_loss_bps:1,review_period_seconds:3600,evidence_sources:[{origin_id:'studionet-explorer',exact_host:'explorer-studio.genlayer.com',path_prefix:'/address/',source_type:1,technical_anchor:true},{origin_id:'proofhalt-repository',exact_host:'github.com',path_prefix:'/haris4587/ProofHalt/',source_type:2,technical_anchor:false}],snapshot_hosts:['explorer-studio.genlayer.com','raw.githubusercontent.com']};
  const canonical=canonicalize(constitution);$('constitutionInput').value=JSON.stringify(constitution,null,2);$('constitutionHash').value=await sha256(canonical);$('constitutionUri').value='https://raw.githubusercontent.com/haris4587/ProofHalt/main/docs/live_constitution.json';
}

const actionConfig={
  register_protocol:{address:()=>CONTRACT_ADDRESS,args:async f=>{const c=await constitutionPayload(f.constitution.value);if(c.hash!==f.constitutionHash.value.toLowerCase())throw new Error('Constitution hash does not match canonical JSON');return [f.protocolId.value.trim(),f.target.value.trim(),f.guardian.value.trim(),f.metadata.value.trim(),f.constitution.value,c.hash,f.constitutionUri.value.trim()]},readback:async f=>readContract(CONTRACT_ADDRESS,'get_protocol',[f.protocolId.value.trim()])},
  activate_protocol:{address:()=>CONTRACT_ADDRESS,args:async f=>[f.protocolId.value.trim()],readback:async f=>readContract(CONTRACT_ADDRESS,'get_protocol',[f.protocolId.value.trim()])},
  publish_constitution:{address:()=>CONTRACT_ADDRESS,args:async f=>{const c=await constitutionPayload(f.constitution.value);if(c.hash!==f.constitutionHash.value.toLowerCase())throw new Error('Constitution hash does not match canonical JSON');return [f.protocolId.value.trim(),f.constitution.value,c.hash,f.constitutionUri.value.trim()]},readback:async f=>readContract(CONTRACT_ADDRESS,'get_pending_constitution',[f.protocolId.value.trim()])},
  activate_pending_constitution:{address:()=>CONTRACT_ADDRESS,args:async f=>[f.protocolId.value.trim()],readback:async f=>readContract(CONTRACT_ADDRESS,'get_active_constitution',[f.protocolId.value.trim()])},
  open_incident:{address:()=>CONTRACT_ADDRESS,args:async f=>[f.protocolId.value.trim(),f.claim.value.trim()],readback:async f=>readContract(CONTRACT_ADDRESS,'get_protocol_incidents',[f.protocolId.value.trim()])},
  submit_evidence:{address:()=>CONTRACT_ADDRESS,args:async f=>{assertSourceSnapshotBinding(f.sourceUrl.value,f.snapshotUri.value);return [f.incidentId.value.trim(),f.originId.value.trim(),f.sourceUrl.value.trim(),f.snapshotUri.value.trim(),f.contentHash.value.toLowerCase(),Number(f.phase.value),f.note.value.trim()]},readback:async f=>readContract(CONTRACT_ADDRESS,'get_incident',[f.incidentId.value.trim()])},
  adjudicate_incident:{address:()=>CONTRACT_ADDRESS,args:async f=>[f.incidentId.value.trim()],readback:async f=>readContract(CONTRACT_ADDRESS,'get_latest_verdict',[f.incidentId.value.trim()])},
  apply_target_patch:{address:f=>f.target.value.trim(),functionName:'apply_one_way_patch',args:async()=>[],readback:async f=>readContract(f.target.value.trim(),'get_security_state',[])},
  submit_remediation:{address:()=>CONTRACT_ADDRESS,args:async f=>{assertSourceSnapshotBinding(f.sourceUrl.value,f.snapshotUri.value);return [f.incidentId.value.trim(),f.originId.value.trim(),f.sourceUrl.value.trim(),f.snapshotUri.value.trim(),f.contentHash.value.toLowerCase(),f.note.value.trim()]},readback:async f=>readContract(CONTRACT_ADDRESS,'get_incident',[f.incidentId.value.trim()])},
  adjudicate_remediation:{address:()=>CONTRACT_ADDRESS,args:async f=>[f.incidentId.value.trim()],readback:async f=>readContract(CONTRACT_ADDRESS,'get_latest_verdict',[f.incidentId.value.trim()])},
  confirm_target_state:{address:()=>CONTRACT_ADDRESS,args:async f=>[f.incidentId.value.trim()],readback:async f=>readContract(CONTRACT_ADDRESS,'get_incident',[f.incidentId.value.trim()])},
  close_incident:{address:()=>CONTRACT_ADDRESS,args:async f=>[f.incidentId.value.trim()],readback:async f=>readContract(CONTRACT_ADDRESS,'get_incident',[f.incidentId.value.trim()])},
};

async function runWrite(form,action){
  if(!connectedAddress){setMessage('Connect MetaMask before submitting a transaction.','error');await connectWallet();if(!connectedAddress)return}
  const provider=window.ethereum;const config=actionConfig[action];const button=form.querySelector('button[type=submit]');button.disabled=true;
  try{
    await ensureStudionet(provider);const args=await config.args(form.elements);const address=config.address(form.elements);const functionName=config.functionName||action;
    const result=await submitAndFinalize({address,account:connectedAddress,provider,functionName,args,onLifecycle:event=>addLog(event.state,`${functionName}: ${event.label}`,event.receipt?.txExecutionResultName||'',event.hash)});
    const state=await config.readback(form.elements);showRead(`${functionName} · finalized state readback`,state);addLog('finalized',`${functionName}: state readback verified`,result.finalized.txExecutionResultName||'FINISHED_WITH_RETURN',result.hash);setMessage(`${functionName} finalized and the resulting contract state was read back successfully.`,'success');
    if(action==='open_incident'){const ids=normalize(state);const latest=Array.isArray(ids)?ids.at(-1):'';document.querySelectorAll('[name=incidentId]').forEach(input=>{if(latest)input.value=latest})}
    await refreshPublicRecord();
  }catch(error){addLog('error',`${action}: failed`,errorMessage(error),error.hash||'');setMessage(`${action} failed: ${errorMessage(error)}`,'error');if(error.receipt)showRead(`${action} · failed finalized receipt`,error.receipt)}
  finally{button.disabled=false}
}

async function readIncident(form){
  const id=form.elements.incidentId.value.trim();const button=form.querySelector('button');button.disabled=true;
  try{const [incident,verdict,evidence]=await Promise.all([readContract(CONTRACT_ADDRESS,'get_incident',[id]),readContract(CONTRACT_ADDRESS,'get_latest_verdict',[id]),readContract(CONTRACT_ADDRESS,'get_incident_evidence',[id])]);showRead(`${id} · authoritative finalized record`,{incident:normalize(incident),verdict:normalize(verdict),evidence_ids:normalize(evidence)});addLog('finalized',`${id}: finalized record loaded`)}
  catch(error){addLog('error',`${id}: read failed`,errorMessage(error))}finally{button.disabled=false}
}

async function refreshPublicRecord(){
  $('recordContract').textContent=shortAddress(CONTRACT_ADDRESS);$('recordContractLink').href=`${EXPLORER}/address/${CONTRACT_ADDRESS}`;$('contractHeroLink').href=`${EXPLORER}/address/${CONTRACT_ADDRESS}`;$('contractHeroLink').target='_blank';$('contractHeroLink').rel='noreferrer';
  if(!PUBLIC_RECORD.protocolId||!PUBLIC_RECORD.incidentId){$('recordProtocol').textContent='Publication in progress';$('recordProtocolState').textContent='Contract verified; preserved case pending';$('recordIncident').textContent='—';$('recordIncidentState').textContent='—';$('recordAction').textContent='—';$('recordConsensus').textContent='—';$('publicRecordDetails').textContent='The live contract is readable now. A complete public incident record will appear here after the authorized Studionet workflow is finalized.';return}
  try{
    const [protocol,incident,verdict,evidence]=await Promise.all([readContract(CONTRACT_ADDRESS,'get_protocol',[PUBLIC_RECORD.protocolId]),readContract(CONTRACT_ADDRESS,'get_incident',[PUBLIC_RECORD.incidentId]),readContract(CONTRACT_ADDRESS,'get_latest_verdict',[PUBLIC_RECORD.incidentId]),readContract(CONTRACT_ADDRESS,'get_incident_evidence',[PUBLIC_RECORD.incidentId])].map(p=>p.then(normalize)));
    $('recordProtocol').textContent=protocol.protocol_id;$('recordProtocolState').textContent=protocolStatuses[protocol.status]||`STATUS ${protocol.status}`;$('recordIncident').textContent=incident.incident_id;$('recordIncidentState').textContent=incidentStatuses[incident.status]||`STATUS ${incident.status}`;$('recordAction').textContent=actionNames[verdict.authorized_action]||`ACTION ${verdict.authorized_action}`;$('recordConsensus').textContent=`revision ${verdict.revision_number} · ${verdict.verified_origin_ids?.length||0} verified origins`;$('publicRecordDetails').textContent=safeJson({protocol,incident,latest_verdict:verdict,evidence_ids:evidence});
  }catch(error){$('publicRecordDetails').textContent=`Could not read the preserved record: ${errorMessage(error)}`}
}

document.querySelectorAll('form[data-action]').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();runWrite(form,form.dataset.action)}));
document.querySelectorAll('form[data-read=incident]').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();readIncident(form)}));
$('generateConstitutionBtn').addEventListener('click',()=>generateConstitution().catch(error=>setMessage(errorMessage(error),'error')));
$('clearLogBtn').addEventListener('click',()=>{txLog.innerHTML='<li class="empty">Transaction monitor cleared.</li>';readResult.textContent='Finalized contract reads will appear here.'});
$('refreshRecordBtn').addEventListener('click',refreshPublicRecord);walletBtn.addEventListener('click',connectWallet);navWalletBtn.addEventListener('click',connectWallet);verifyContractBtn.addEventListener('click',()=>verifyLiveContract().catch(()=>{}));
if(window.ethereum){window.ethereum.on?.('accountsChanged',accounts=>{if(!accounts?.[0])disconnectUi();else{connectedAddress=accounts[0];walletStatus.textContent=shortAddress(connectedAddress);navWalletLabel.textContent=shortAddress(connectedAddress)}});window.ethereum.on?.('chainChanged',refreshNetwork)}
refreshNetwork();verifyLiveContract().catch(()=>{});refreshPublicRecord();
