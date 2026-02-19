import { useState, useEffect } from "react";
import VideoFeed from "./components/VideoFeed";
import Controls from "./components/Controls";
import Stats from "./components/Stats";
import AlertLog from "./components/AlertLog";
import "./App.css";

const API = "http://localhost:8000";
const WS = "ws://localhost:8000";

export default function App() {
  const [mode, setMode] = useState(null); // "webcam" | "video"
  const [fileId, setFileId] = useState(null);
  const [useCase, setUseCase] = useState("traffic");
  const [stats, setStats] = useState({ fps: 0, counts: {}, total: 0, total_tracked: 0 });
  const [wsUrl, setWsUrl] = useState(null);
  const [streaming, setStreaming] = useState(false);
  const [logs, setLogs] = useState([]);

  // Fetch logs every 3s when streaming
  useEffect(() => {
    if (!streaming) return;
    const interval = setInterval(async () => {
      const res = await fetch(`${API}/logs?limit=50`);
      const data = await res.json();
      setLogs(data.reverse());
    }, 3000);
    return () => clearInterval(interval);
  }, [streaming]);

  const switchUseCase = async (name) => {
    await fetch(`${API}/use-case/${name}`, { method: "POST" });
    setUseCase(name);
  };

  const startWebcam = () => {
    setMode("webcam");
    setWsUrl(`${WS}/ws/stream`);
    setStreaming(true);
  };

  const startVideo = (id) => {
    setFileId(id);
    setMode("video");
    setWsUrl(`${WS}/ws/video/${id}`);
    setStreaming(true);
  };

  const stop = async () => {
    setStreaming(false);
    setWsUrl(null);
    setMode(null);
    setFileId(null);
    await fetch(`${API}/reset`, { method: "POST" });
    setStats({ fps: 0, counts: {}, total: 0, total_tracked: 0 });
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo-mark">⬡</div>
          <div>
            <h1 className="title">SENTINEL</h1>
            <p className="subtitle">Real-Time Object Detection System</p>
          </div>
        </div>
        <div className="header-right">
          <div className={`status-pill ${streaming ? "active" : "idle"}`}>
            <span className="status-dot" />
            {streaming ? "LIVE" : "STANDBY"}
          </div>
        </div>
      </header>

      <main className="main">
        <div className="left-panel">
          <VideoFeed wsUrl={wsUrl} onStats={setStats} streaming={streaming} />
          <Controls
            streaming={streaming}
            useCase={useCase}
            onSwitchUseCase={switchUseCase}
            onStartWebcam={startWebcam}
            onStartVideo={startVideo}
            onStop={stop}
            api={API}
          />
        </div>
        <div className="right-panel">
          <Stats stats={stats} useCase={useCase} />
          <AlertLog logs={logs} />
        </div>
      </main>
    </div>
  );
}