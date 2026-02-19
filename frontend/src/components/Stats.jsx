import "./Stats.css";

const CLASS_COLORS = {
  car: "#00ff88", bus: "#00e5ff", truck: "#ff3b5c",
  motorcycle: "#ffd600", bicycle: "#ff9100",
  "traffic light": "#00e5ff", "stop sign": "#ff3b5c",
  person: "#c8d8e8", backpack: "#ffd600", handbag: "#ff9100", suitcase: "#00ff88",
  bird: "#00ff88", cat: "#ffd600", dog: "#ff9100", horse: "#00e5ff",
  elephant: "#c8d8e8", bear: "#ff3b5c", zebra: "#ffffff", giraffe: "#ffd600",
  bottle: "#00ff88", cup: "#00e5ff", airplane: "#00e5ff", train: "#ff9100",
};

function getColor(cls) {
  return CLASS_COLORS[cls] || "#c8d8e8";
}

export default function Stats({ stats, useCase }) {
  const { fps, counts = {}, total = 0, total_tracked = 0 } = stats;
  const maxCount = Math.max(...Object.values(counts), 1);

  return (
    <div className="panel stats-panel">
      <div className="panel-header">
        <span className="panel-label">Detection Stats</span>
        <span className="use-case-tag">{useCase.toUpperCase()}</span>
      </div>
      <div className="stats-body">

        {/* FPS + totals */}
        <div className="metrics-row">
          <div className="metric">
            <div className="metric-value fps-val">{fps || 0}</div>
            <div className="metric-label">FPS</div>
          </div>
          <div className="metric">
            <div className="metric-value">{total}</div>
            <div className="metric-label">In Frame</div>
          </div>
          <div className="metric">
            <div className="metric-value">{total_tracked}</div>
            <div className="metric-label">Tracked</div>
          </div>
        </div>

        {/* Per-class bars */}
        <div className="class-bars">
          {Object.entries(counts).length === 0 ? (
            <p className="no-data">No detections yet</p>
          ) : (
            Object.entries(counts).map(([cls, cnt]) => (
              <div className="class-row" key={cls}>
                <div className="class-name">{cls}</div>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${(cnt / maxCount) * 100}%`,
                      background: getColor(cls),
                    }}
                  />
                </div>
                <div className="class-count" style={{ color: getColor(cls) }}>
                  {cnt}
                </div>
              </div>
            ))
          )}
        </div>

      </div>
    </div>
  );
}
