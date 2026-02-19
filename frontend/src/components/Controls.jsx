import { useRef, useState } from "react";
import "./Controls.css";

const USE_CASES = [
  { id: "traffic",  label: "Traffic",    icon: "🚗" },
  { id: "security", label: "Security",   icon: "👁" },
  { id: "wildlife", label: "Wildlife",   icon: "🐘" },
  { id: "retail",   label: "Retail",     icon: "🛍" },
  { id: "airport",  label: "Airport/Rail", icon: "✈" },
];

export default function Controls({
  streaming, useCase, onSwitchUseCase,
  onStartWebcam, onStartVideo, onStop, api,
}) {
  const fileRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadName, setUploadName] = useState(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadName(file.name);
    const form = new FormData();
    form.append("file", file);
    const res  = await fetch(`${api}/upload`, { method: "POST", body: form });
    const data = await res.json();
    setUploading(false);
    if (data.file_id) onStartVideo(data.file_id);
  };

  return (
    <div className="panel controls-panel">
      <div className="panel-header">
        <span className="panel-label">Controls</span>
      </div>
      <div className="controls-body">

        {/* Use case switcher */}
        <div className="section">
          <div className="section-label">Detection Mode</div>
          <div className="use-case-grid">
            {USE_CASES.map((uc) => (
              <button
                key={uc.id}
                className={`uc-btn ${useCase === uc.id ? "uc-active" : ""}`}
                onClick={() => onSwitchUseCase(uc.id)}
                disabled={streaming}
              >
                <span className="uc-icon">{uc.icon}</span>
                <span>{uc.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Source selection */}
        <div className="section">
          <div className="section-label">Input Source</div>
          <div className="source-row">
            {!streaming ? (
              <>
                <button className="btn btn-cyan" onClick={onStartWebcam}>
                  📷 Webcam
                </button>
                <button
                  className="btn btn-green"
                  onClick={() => fileRef.current.click()}
                  disabled={uploading}
                >
                  {uploading ? "Uploading…" : "📂 Video File"}
                </button>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".mp4,.avi,.mov,.mkv"
                  style={{ display: "none" }}
                  onChange={handleFileUpload}
                />
              </>
            ) : (
              <button className="btn btn-red" onClick={onStop}>
                ⏹ Stop
              </button>
            )}
          </div>
          {uploadName && !streaming && (
            <p className="upload-name">Ready: {uploadName}</p>
          )}
        </div>

      </div>
    </div>
  );
}
