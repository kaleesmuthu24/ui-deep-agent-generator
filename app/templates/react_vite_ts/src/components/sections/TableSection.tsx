import { useEffect, useMemo, useState } from 'react';
import { getOperationStub } from '../../generated/opmap';

export function TableSection({ title, operationId }: { title: string; operationId: string }) {
  const [status, setStatus] = useState<'idle'|'loading'|'done'|'error'>('idle');
  const [rows, setRows] = useState<any[]>([]);
  const [error, setError] = useState<string>('');

  const op = useMemo(() => getOperationStub(operationId), [operationId]);

  useEffect(() => {
    let mounted = true;
    const run = async () => {
      setStatus('loading');
      setError('');
      try {
        const data = await op.call(undefined);
        const list = Array.isArray(data) ? data : (data?.items || data?.data || []);
        if (mounted) {
          setRows(Array.isArray(list) ? list : []);
          setStatus('done');
        }
      } catch (e: any) {
        if (mounted) {
          setError(e?.message || String(e));
          setStatus('error');
        }
      }
    };
    run();
    return () => { mounted = false; };
  }, [op]);

  if (status === 'error') {
    return <div className="card"><p style={{ color: 'var(--danger)' }}>{error}</p></div>;
  }

  const cols = Object.keys(rows?.[0] || {}).slice(0, 8);

  return (
    <div className="grid">
      <div style={{ color: 'var(--muted)' }}>
        {status === 'loading' ? 'Loading…' : `${rows.length} row(s)`}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {cols.map((c) => (
                <th key={c} style={{ textAlign: 'left', padding: '10px 8px', borderBottom: '1px solid var(--border)' }}>
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 50).map((r, idx) => (
              <tr key={idx}>
                {cols.map((c) => (
                  <td key={c} style={{ padding: '10px 8px', borderBottom: '1px solid var(--border)' }}>
                    {typeof r?.[c] === 'object' ? JSON.stringify(r?.[c]) : String(r?.[c] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p style={{ color: 'var(--muted)', margin: 0 }}>
        This table is heuristic. Refine columns + paging as needed.
      </p>
    </div>
  );
}
