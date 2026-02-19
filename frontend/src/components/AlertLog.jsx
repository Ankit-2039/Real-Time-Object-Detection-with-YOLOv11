import "./AlertLog.css";

export default function AlertLog({ logs }) {
  return (
    <div className="panel log-panel">
      <div className="panel-header">
        <span className="panel-label">Detection Log</span>
        <span className="log-count">{logs.length} entries</span>
      </div>
      <div className="log-body">
        {logs.length === 0 ? (
          <p className="log-empty">Awaiting detections…</p>
        ) : (
          <table className="log-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Class</th>
                <th>Conf</th>
                <th>Speed</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((row, i) => (
                <tr key={i} className={i === 0 ? "log-new" : ""}>
                  <td className="mono">#{row.track_id}</td>
                  <td className="cls-cell">{row.class}</td>
                  <td className="mono conf">{parseFloat(row.confidence).toFixed(2)}</td>
                  <td className="mono">{parseFloat(row.speed_kmh).toFixed(0)} km/h</td>
                  <td className="mono time">{row.timestamp?.slice(11, 19)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
