const steps=[
 {status:'EVIDENCE',title:'Evidence retrieved',text:'Two independent origins fetched; submitted hashes match immutable evidence snapshots.'},
 {status:'HALT AUTHORIZED',title:'Critical exploit corroborated',text:'Target, impact, source independence, integrity and technical-anchor gates all pass.'},
 {status:'HALTED',title:'Guardian pause confirmed',text:'Incident-specific Guardian state confirms the bound halt revision; target is paused.'},
 {status:'PATCHED',title:'Remediation verified',text:'A one-way target patch is applied while paused and new remediation artifacts are submitted.'},
 {status:'RESTORE AUTHORIZED',title:'Recovery consensus finalized',text:'Independent remediation evidence confirms the exploit is no longer active.'},
 {status:'RECOVERED',title:'Restore confirmed',text:'Guardian confirms the incident-specific restore. No other active incident remains.'}
];
let i=0;const timeline=document.getElementById('timeline'),pill=document.getElementById('statusPill'),advance=document.getElementById('advanceBtn'),reset=document.getElementById('resetBtn');
function render(){if(i===0){timeline.innerHTML='<div class="event"><time>READY</time><div><b>Simulation staged</b><span>No live wallet writes are performed by this reviewer demo.</span></div></div>';pill.textContent='READY';advance.textContent='Begin evidence scan';return}timeline.innerHTML=steps.slice(0,i).map((s,n)=>`<div class="event"><time>STEP ${String(n+1).padStart(2,'0')}</time><div><b>${s.title}</b><span>${s.text}</span></div></div>`).join('');pill.textContent=steps[i-1].status;advance.textContent=i===steps.length?'Demo complete':'Advance lifecycle';advance.disabled=i===steps.length}
advance.addEventListener('click',()=>{if(i<steps.length)i++;render()});reset.addEventListener('click',()=>{i=0;advance.disabled=false;render()});render();