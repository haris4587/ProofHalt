import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

const readClient = createClient({ chain: studionet });

export function readGlobalConstitution(address) {
  return readClient.readContract({
    address,
    functionName: 'get_global_constitution',
    args: []
  });
}
