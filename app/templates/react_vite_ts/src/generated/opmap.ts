import * as ops from '../api/operations';

/**
 * The generator stubs `operations.ts` based on operationIds found in ui-spec.
 * This adapter returns a callable with a consistent interface.
 */
export function getOperationStub(operationId: string): { call: (payload?: unknown) => Promise<any> } {
  const fn = (ops as any)[toFnName(operationId)];
  if (typeof fn === 'function') {
    return { call: (payload?: unknown) => fn(payload) };
  }
  return {
    call: async () => {
      throw new Error(`No operation stub for operationId="${operationId}". Update src/api/operations.ts.`);
    }
  };
}

function toFnName(operationId: string) {
  const pascal = operationId
    .replace(/[^a-zA-Z0-9]+/g, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)
    .map((p) => p.slice(0,1).toUpperCase() + p.slice(1))
    .join('');
  return pascal.slice(0,1).toLowerCase() + pascal.slice(1);
}
