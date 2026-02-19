import { useEffect, useRef, useCallback } from "react";
import "./VideoFeed.css";

export default function VideoFeed({ wsUrl, onStats, streaming }) {
  const imgRef = useRef(null);
  const wsRef  = useRef(null);

  const connect = useCallback(() => {
    if (!wsUrl) return;
    const ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer";

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.error) { console.error("WS error:", data.error); return; }
      if (data.done)  { return; }
      if (imgRef.current && data.frame) {
        imgRef.current.src = `data:image/jpeg;base64,${data.frame}`;
      }
      if (data.stats) onStats(data.stats);
    };

    ws.onerror = (e) => console.error("WebSocket error", e);
    ws.onclose = () => { wsRef.current = null; };
    wsRef.current = ws;
  }, [wsUrl, onStats]);

  useEffect(() => {
    if (streaming && wsUrl) {
      connect();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [streaming, wsUrl, connect]);

  return (
    <div className="panel feed-panel">
      <div className="panel-header">
        <span className="panel-label">Video Feed</span>
        {streaming && <span className="feed-badge">● REC</span>}
      </div>
      <div className="feed-body">
        {streaming ? (
          <img ref={imgRef} className="feed-img" alt="Detection feed" />
        ) : (
          <div className="feed-placeholder">
            <div className="placeholder-icon">⬡</div>
            <p>Select a source to begin detection</p>
          </div>
        )}
      </div>
    </div>
  );
}
