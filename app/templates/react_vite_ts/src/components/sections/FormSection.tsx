import { useMemo, useState } from 'react';
import { getOperationStub } from '../../generated/opmap';

export function FormSection({ title, operationId }: { title: string; operationId: string }) {
  const [raw, setRaw] = useState<string>('{}');
  const [status, setStatus] = useState<'idle'|'running'|'done'|'error'>('idle');
  const [result, setResult] = useState<string>('');

  const op = useMemo(() => getOperationStub(operationId), [operationId]);

  const submit = async () => {
    setStatus('running');
    setResult('');
    try {
      const payload = JSON.parse(raw || '{}');
      const data = await op.call(payload);
      setResult(JSON.stringify(data, null, 2));
      setStatus('done');
    } catch (e: any) {
      setResult(e?.message || String(e));
      setStatus('error');
    }
  };

  return (
    <div className="grid">
      <div>
        <label className="label">Request JSON</label>
        <textarea
          className="input"
          rows={8}
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          aria-label={`${title} request json`}
        />
      </div>
      <div style={{ display: 'flex', gap: 10 }}>
        <button className="btn" onClick={submit} type="button">
          Run
        </button>
        <button className="btn secondary" onClick={() => setRaw('{}')} type="button">
          Reset
        </button>
      </div>
      <div>
        <label className="label">Result</label>
        <pre className="input" style={{ whiteSpace: 'pre-wrap', margin: 0 }} aria-label={`${title} result`}>
{status === 'idle' ? 'Ready.' : result}
        </pre>
      </div>
      <p style={{ color: 'var(--muted)', margin: 0 }}>
        This is a generic form runner. Replace it with schema-driven fields for production.
      </p>
    </div>
  );
}
