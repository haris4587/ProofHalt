import json, sys
from pathlib import Path

path=Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/proofhalt_stage9/solc_output.json')
data=json.loads(path.read_text())
messages=data.get('errors',[])
errors=[m for m in messages if m.get('severity')=='error']
warnings=[m for m in messages if m.get('severity')=='warning']
for m in messages:
    print(m.get('severity','info').upper(), m.get('formattedMessage',m.get('message','')).strip())
if errors:
    print(f'COMPILE FAIL: {len(errors)} Solidity error(s)')
    raise SystemExit(1)
contracts=data.get('contracts',{})
required=[('ProofHaltGuardian.sol','ProofHaltGuardian'),('DemoVault.sol','DemoVault')]
for source,name in required:
    try: c=contracts[source][name]
    except KeyError:
        print('COMPILE FAIL: missing artifact',source,name); raise SystemExit(1)
    bytecode=c['evm']['bytecode']['object']; runtime=c['evm']['deployedBytecode']['object']
    if not bytecode or not runtime:
        print('COMPILE FAIL: empty bytecode',name); raise SystemExit(1)
    runtime_bytes=len(runtime)//2
    if runtime_bytes >= 24576:
        print('COMPILE FAIL: EIP-170 runtime too large',name,runtime_bytes); raise SystemExit(1)
    print(f'ARTIFACT {name}: creation={len(bytecode)//2} bytes runtime={runtime_bytes} bytes ABI={len(c["abi"])} entries')
    mids=c['evm'].get('methodIdentifiers',{})
    print('  methods:', ', '.join(sorted(mids)))

expected_guardian={
 'proofHaltAuthority()','protectedTarget()','activeHaltCount()','isPaused()',
 'isIncidentActive(string)','isIncidentRestored(string)',
 'pauseFromProofHalt(string,uint32)','restoreFromProofHalt(string,uint32)',
 'incidentState(string)','actionExecuted(string,uint32,bool)','incidentHashOf(string)'
}
expected_vault={
 'configurationAuthority()','proofHaltGuardian()','isProofHaltConfigured()','paused()',
 'deposit()','withdraw(uint256)','balanceOf(address)','proofHaltPause()','proofHaltRestore()',
 'demoExploitEnabled()','DEMO_MAX_EXPLOIT_PER_CALL()','demoExploitWithdrawFrom(address,uint256)',
 'applyDemoPatch()','totalManagedAssets()'
}
g=contracts['ProofHaltGuardian.sol']['ProofHaltGuardian']['evm']['methodIdentifiers']
v=contracts['DemoVault.sol']['DemoVault']['evm']['methodIdentifiers']
for name,expected,actual in [('Guardian',expected_guardian,set(g)),('DemoVault',expected_vault,set(v))]:
    miss=expected-actual
    if miss:
        print('COMPILE FAIL:',name,'missing ABI methods',sorted(miss)); raise SystemExit(1)
print(f'COMPILE PASS: 0 errors, {len(warnings)} warning(s), required ABI present, bytecode-size gates passed')
