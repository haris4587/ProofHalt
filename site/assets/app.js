const CONTRACT_ADDRESS='0x9E43C93Dae87C32eEadbD8E733FAb4e54cF06767';
const STUDIONET_CHAIN_ID=61999;
const STUDIONET_CHAIN_HEX='0xF22F';
const STUDIONET_RPC='https://studio.genlayer.com/api';
const EXPLORER='https://explorer-studio.genlayer.com';

const steps=[
 {status:'EVIDENCE',title:'Evidence retrieved',text:'Two independent origins fetched; submitted hashes match immutable evidence snapshots.'},
 {status:'HALT AUTHORIZED',title:'Critical exploit corroborated',text:'Target, impact, source independence, integrity and technical-anchor gates all pass.'},
 {status:'HALTED',title:'Guardian pause confirmed',text:'Incident-specific Guardian state confirms the bound halt revision; target is paused.'},
 {status:'PATCHED',title:'Remediation verified',text:'A one-way target patch is applied while paused and new remediation artifacts are submitted.'},
 {status:'RESTORE AUTHORIZED',title:'Recovery consensus finalized',text:'Independent remediation evidence confirms the exploit is no longer active.'},
 {status:'RECOVERED',title:'Restore confirmed',text:'Guardian confirms the incident-specific restore. No other active incident remains.'}
];

let i=0;
let connectedAddress='';
let sdkPromise=null;

const timeline=document.getElementById('timeline');
const pill=document.getElementById('statusPill');
const advance=document.getElementById('advanceBtn');
const reset=document.getElementById('resetBtn');
const navWalletBtn=document.getElementById('navWalletBtn');
const navWalletLabel=document.getElementById('navWalletLabel');
const walletBtn=document.getElementById('walletBtn');
const verifyContractBtn=document.getElementById('verifyContractBtn');
const walletStatus=document.getElementById('walletStatus');
const networkStatus=document.getElementById('networkStatus');
const contractStatus=document.getElementById('contractStatus');
const constitutionStatus=document.getElementById('constitutionStatus');
const walletMessage=document.getElementById('walletMessage');

function shortAddress(address){return address?`${address.slice(0,6)}…${address.slice(-4)}`:''}
function setMessage(message,tone='muted'){
  walletMessage.textContent=message;
  walletMessage.dataset.tone=tone;
}
function normalizeContractValue(value){
  if(typeof value==='string'){
    try{return JSON.parse(value)}catch{return value}
  }
  return value;
}
async function loadGenLayerSdk(){
  if(!sdkPromise){
    sdkPromise=Promise.all([
      import('https://esm.sh/genlayer-js@1.1.8'),
      import('https://esm.sh/genlayer-js@1.1.8/chains')
    ]).then(([sdk,chains])=>({createClient:sdk.createClient,studionet:chains.studionet}));
  }
  return sdkPromise;
}
async function ensureStudionet(provider){
  try{
    await provider.request({method:'wallet_switchEthereumChain',params:[{chainId:STUDIONET_CHAIN_HEX}]});
  }catch(error){
    if(error&&Number(error.code)===4902){
      await provider.request({
        method:'wallet_addEthereumChain',
        params:[{
          chainId:STUDIONET_CHAIN_HEX,
          chainName:'GenLayer Studionet',
          nativeCurrency:{name:'GEN',symbol:'GEN',decimals:18},
          rpcUrls:[STUDIONET_RPC],
          blockExplorerUrls:[EXPLORER]
        }]
      });
      return;
    }
    throw error;
  }
}
async function refreshNetwork(){
  if(!window.ethereum)return;
  try{
    const chainHex=await window.ethereum.request({method:'eth_chainId'});
    const chainId=parseInt(chainHex,16);
    networkStatus.textContent=chainId===STUDIONET_CHAIN_ID?'Studionet · chain 61999':`Wrong network · chain ${chainId}`;
    networkStatus.classList.toggle('ok',chainId===STUDIONET_CHAIN_ID);
  }catch{
    networkStatus.textContent='Network unavailable';
  }
}
async function verifyLiveContract(){
  verifyContractBtn.disabled=true;
  contractStatus.textContent='Reading finalized contract…';
  constitutionStatus.textContent='Loading…';
  setMessage('Reading ProofHalt directly from GenLayer Studionet…');
  try{
    const {createClient,studionet}=await loadGenLayerSdk();
    const readClient=createClient({chain:studionet});
    const raw=await readClient.readContract({
      address:CONTRACT_ADDRESS,
      functionName:'get_global_constitution',
      args:[]
    });
    const data=normalizeContractValue(raw);
    if(!data||typeof data!=='object')throw new Error('Unexpected contract response');
    const groups=Number(data.minimum_independent_groups ?? 0);
    const anchor=data.technical_anchor_required===true;
    const schema=String(data.schema||'proofhalt');
    contractStatus.textContent=`Verified · ${shortAddress(CONTRACT_ADDRESS)}`;
    contractStatus.classList.add('ok');
    constitutionStatus.textContent=`${groups||'?'} groups · ${anchor?'technical anchor required':'anchor policy unavailable'}`;
    constitutionStatus.classList.toggle('ok',Boolean(groups)&&anchor);
    setMessage(`Live contract read succeeded (${schema}). This verifies the deployed GenLayer state; the Guardian lifecycle below remains a staged walkthrough.`, 'success');
  }catch(error){
    contractStatus.textContent='Verification failed';
    constitutionStatus.textContent='Not loaded';
    contractStatus.classList.remove('ok');
    constitutionStatus.classList.remove('ok');
    const detail=error instanceof Error?error.message:'Unknown error';
    setMessage(`Could not read the live GenLayer contract: ${detail}`,'error');
  }finally{
    verifyContractBtn.disabled=!connectedAddress;
  }
}
async function connectWallet(){
  const provider=window.ethereum;
  if(!provider){
    setMessage('MetaMask was not detected. Install MetaMask or open this page inside the MetaMask browser, then try again.','error');
    window.open('https://metamask.io/download/','_blank','noopener,noreferrer');
    return;
  }
  walletBtn.disabled=true;
  navWalletBtn.disabled=true;
  walletStatus.textContent='Waiting for MetaMask…';
  setMessage('Approve the connection request in MetaMask.');
  try{
    const accounts=await provider.request({method:'eth_requestAccounts'});
    if(!Array.isArray(accounts)||!accounts[0])throw new Error('No wallet account was selected');
    connectedAddress=accounts[0];
    await ensureStudionet(provider);
    const {createClient,studionet}=await loadGenLayerSdk();
    const walletClient=createClient({chain:studionet,account:connectedAddress,provider});
    await walletClient.connect('studionet');
    walletStatus.textContent=shortAddress(connectedAddress);
    walletStatus.classList.add('ok');
    navWalletLabel.textContent=shortAddress(connectedAddress);
    navWalletBtn.classList.add('connected');
    walletBtn.textContent='Wallet connected';
    walletBtn.classList.add('connected');
    verifyContractBtn.disabled=false;
    await refreshNetwork();
    setMessage('MetaMask connected to GenLayer Studionet. Verifying the deployed ProofHalt contract now…','success');
    await verifyLiveContract();
  }catch(error){
    connectedAddress='';
    walletStatus.textContent='Not connected';
    walletStatus.classList.remove('ok');
    verifyContractBtn.disabled=true;
    const detail=error instanceof Error?error.message:'Wallet request failed';
    setMessage(detail.toLowerCase().includes('user rejected')?'The MetaMask request was cancelled. Nothing was submitted.':`Wallet connection failed: ${detail}`,'error');
  }finally{
    walletBtn.disabled=false;
    navWalletBtn.disabled=false;
  }
}
function disconnectUi(){
  connectedAddress='';
  walletStatus.textContent='Not connected';
  walletStatus.classList.remove('ok');
  navWalletLabel.textContent='Connect MetaMask';
  navWalletBtn.classList.remove('connected');
  walletBtn.textContent='Connect MetaMask';
  walletBtn.classList.remove('connected');
  verifyContractBtn.disabled=true;
  contractStatus.textContent='Awaiting verification';
  contractStatus.classList.remove('ok');
  constitutionStatus.textContent='Not loaded';
  constitutionStatus.classList.remove('ok');
  setMessage('Wallet disconnected. Reconnect MetaMask to verify the live ProofHalt deployment.');
}
function render(){
  if(i===0){
    timeline.innerHTML='<div class="event"><time>READY</time><div><b>Reviewer walkthrough staged</b><span>Connect MetaMask above to verify the live GenLayer contract. The incident lifecycle itself is a transparent simulation of the external Guardian path.</span></div></div>';
    pill.textContent='READY';
    advance.textContent='Begin evidence scan';
    return;
  }
  timeline.innerHTML=steps.slice(0,i).map((s,n)=>`<div class="event"><time>STEP ${String(n+1).padStart(2,'0')}</time><div><b>${s.title}</b><span>${s.text}</span></div></div>`).join('');
  pill.textContent=steps[i-1].status;
  advance.textContent=i===steps.length?'Demo complete':'Advance lifecycle';
  advance.disabled=i===steps.length;
}

advance.addEventListener('click',()=>{if(i<steps.length)i++;render()});
reset.addEventListener('click',()=>{i=0;advance.disabled=false;render()});
walletBtn.addEventListener('click',connectWallet);
navWalletBtn.addEventListener('click',connectWallet);
verifyContractBtn.addEventListener('click',verifyLiveContract);

if(window.ethereum){
  window.ethereum.on?.('accountsChanged',(accounts)=>{
    if(!Array.isArray(accounts)||!accounts[0]){disconnectUi();return}
    connectedAddress=accounts[0];
    walletStatus.textContent=shortAddress(connectedAddress);
    navWalletLabel.textContent=shortAddress(connectedAddress);
  });
  window.ethereum.on?.('chainChanged',refreshNetwork);
}

render();
refreshNetwork();