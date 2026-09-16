import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { ExecutionResult, TransactionStatus } from 'genlayer-js/types';

const readClient = createClient({ chain: studionet });

export function readContract(address, functionName, args = []) {
  return readClient.readContract({ address, functionName, args, jsonSafeReturn: true });
}

export function readGlobalConstitution(address) {
  return readContract(address, 'get_global_constitution');
}

export function getTransaction(hash) {
  return readClient.getTransaction({ hash });
}

export async function submitAndFinalize({
  address,
  account,
  provider,
  functionName,
  args = [],
  onLifecycle = () => {},
}) {
  const writeClient = createClient({ chain: studionet, account, provider });
  onLifecycle({ state: 'wallet', label: 'Waiting for wallet confirmation' });
  const hash = await writeClient.writeContract({
    address,
    functionName,
    args,
    value: 0n,
  });
  onLifecycle({ state: 'submitted', label: 'Transaction submitted', hash });

  const accepted = await readClient.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.ACCEPTED,
    interval: 1500,
    retries: 240,
  });
  onLifecycle({ state: 'consensus', label: 'Consensus result accepted', hash, receipt: accepted });

  const finalized = await readClient.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.FINALIZED,
    interval: 1500,
    retries: 240,
  });
  const result = finalized.txExecutionResultName;
  if (result && result !== ExecutionResult.FINISHED_WITH_RETURN) {
    const error = new Error(`Transaction finalized with ${result}`);
    error.receipt = finalized;
    error.hash = hash;
    throw error;
  }
  onLifecycle({ state: 'finalized', label: 'Finalized on Studionet', hash, receipt: finalized });
  return { hash, accepted, finalized };
}
