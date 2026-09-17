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

function leaderReceipt(transaction) {
  const receipts = transaction?.consensus_data?.leader_receipt
    ?? transaction?.consensusData?.leaderReceipt
    ?? [];
  if (Array.isArray(receipts)) return receipts.at(-1);
  return receipts;
}

export function assertSuccessfulExecution(receipt, transaction) {
  const sdkResult = receipt?.txExecutionResultName;
  if (sdkResult && sdkResult !== ExecutionResult.FINISHED_WITH_RETURN) {
    throw new Error(`Transaction finalized with ${sdkResult}`);
  }

  // Studionet currently omits txExecutionResultName from some finalized SDK
  // receipts. The consensus leader receipt is authoritative in that case.
  const leader = leaderReceipt(transaction);
  const resultStatus = leader?.result?.status;
  const executionStatus = leader?.execution_result ?? leader?.executionResult;
  if (resultStatus && resultStatus !== 'return') {
    const payload = leader?.result?.payload;
    const detail = typeof payload === 'string'
      ? payload
      : payload?.readable ?? payload?.raw ?? resultStatus;
    throw new Error(`Contract execution failed: ${detail}`);
  }
  if (executionStatus && executionStatus !== 'SUCCESS') {
    throw new Error(`Contract execution failed: ${executionStatus}`);
  }
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
  const transaction = await readClient.getTransaction({ hash });
  try {
    assertSuccessfulExecution(finalized, transaction);
  } catch (error) {
    error.receipt = finalized;
    error.transaction = transaction;
    error.hash = hash;
    throw error;
  }
  onLifecycle({ state: 'finalized', label: 'Finalized on Studionet', hash, receipt: finalized });
  return { hash, accepted, finalized, transaction };
}
