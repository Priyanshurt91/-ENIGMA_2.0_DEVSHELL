import { useState, useEffect, useRef } from "react";
import { Badge } from "../components/Shared.jsx";

export default function NiftiViewer({ onNavigate, analysisResult }) {
    const [slice, setSlice] = useState(42);
    const [window_, setWindow] = useState("lung");
    const [overlay, setOverlay] = useState(true);
    const canvasRef = useRef(null);
    const windows = [
        { id: "lung", label: "Lung Window", hu: "-600/1200" },
        { id: "mediastinum", label: "Mediastinum", hu: "40/400" },
        { id: "bone", label: "Bone Window", hu: "400/1800" },
    ];
    const r = analysisResult || {};
    const patientLabel = r.patient_name ? `${r.patient_id || "PT"} · ${r.patient_name}` : "PT-0041 · Ananya Sharma";
    const finding = r.predicted_class || "Suspicious Nodule";
    const conf = r.confidence || 91;

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const W = canvas.width, H = canvas.height;
        ctx.clearRect(0, 0, W, H);
        ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
        const grd = ctx.createRadialGradient(W / 2, H / 2, 10, W / 2, H / 2, 130);
        grd.addColorStop(0, "#2a3a2a"); grd.addColorStop(0.5, "#1a2a1a"); grd.addColorStop(1, "#000");
        ctx.beginPath(); ctx.ellipse(W / 2 - 40, H / 2 + 10, 70 + Math.sin(slice * 0.15) * 5, 90, -0.2, 0, Math.PI * 2); ctx.fillStyle = grd; ctx.fill();
        ctx.beginPath(); ctx.ellipse(W / 2 + 40, H / 2 + 10, 70 + Math.cos(slice * 0.15) * 5, 90, 0.2, 0, Math.PI * 2); ctx.fill();
        const nx = W / 2 - 35, ny = H / 2 - 20;
        if (overlay) {
            const hg = ctx.createRadialGradient(nx, ny, 0, nx, ny, 38);
            hg.addColorStop(0, "rgba(255,68,68,0.7)"); hg.addColorStop(0.4, "rgba(255,140,0,0.4)"); hg.addColorStop(0.7, "rgba(255,217,61,0.2)"); hg.addColorStop(1, "transparent");
            ctx.beginPath(); ctx.arc(nx, ny, 38, 0, Math.PI * 2); ctx.fillStyle = hg; ctx.fill();
        }
        const ng = ctx.createRadialGradient(nx, ny, 0, nx, ny, 14 + Math.sin(slice * 0.2) * 2);
        ng.addColorStop(0, "#fff"); ng.addColorStop(0.3, "#ccc"); ng.addColorStop(1, "#666");
        ctx.beginPath(); ctx.arc(nx, ny, 14 + Math.sin(slice * 0.2) * 2, 0, Math.PI * 2); ctx.fillStyle = ng; ctx.fill();
        ctx.strokeStyle = "rgba(0,255,136,0.5)"; ctx.lineWidth = 0.5; ctx.setLineDash([4, 4]);
        ctx.beginPath(); ctx.moveTo(nx, 0); ctx.lineTo(nx, H); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, ny); ctx.lineTo(W, ny); ctx.stroke(); ctx.setLineDash([]);
        ctx.strokeStyle = "#00ff88"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(nx, ny, 22, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = "#00ff88"; ctx.font = "bold 10px 'DM Mono', monospace";
        ctx.fillText("NODULE", nx + 26, ny - 6); ctx.fillText(`Ø${(14 + Math.sin(slice * 0.2) * 2).toFixed(1)}mm`, nx + 26, ny + 8);
        ctx.fillStyle = "rgba(0,255,136,0.7)"; ctx.font = "9px 'DM Mono', monospace";
        ctx.fillText(`SLICE ${slice}/80`, 8, 16);
        ctx.fillText(window_ === "lung" ? "HU -600/1200" : window_ === "mediastinum" ? "HU 40/400" : "HU 400/1800", 8, 28);
    }, [slice, overlay, window_]);

    return (
        <div className="page-enter" style={{ minHeight: "100vh", padding: "40px 48px 180px", position: "relative", zIndex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 32 }}>
                <div>
                    <div style={{ marginBottom: 6 }}><Badge color="#00b4ff">NiftiViewer · 3D Medical Imaging</Badge></div>
                    <h2 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: 28, color: "#e6edf3" }}>DICOM / NIfTI Viewer</h2>
                </div>
                <button onClick={() => onNavigate("result")} style={{ padding: "10px 20px", background: "rgba(192,132,252,0.1)", border: "1px solid #c084fc44", borderRadius: 7, color: "#c084fc", fontFamily: "'Syne', sans-serif", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>View ResultCard →</button>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 20 }}>
                <div style={{ border: "1px solid #0d1a0d", borderRadius: 10, overflow: "hidden", background: "#000", position: "relative" }}>
                    <canvas ref={canvasRef} width={520} height={400} style={{ width: "100%", height: "auto", display: "block" }} />
                    <div style={{ position: "absolute", top: 0, left: 0, right: 0, padding: "8px 14px", background: "linear-gradient(180deg, rgba(0,0,0,0.8), transparent)", display: "flex", alignItems: "center", gap: 10 }}>
                        <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#00ff88" }}>{patientLabel} · CT · Axial</span>
                        <span style={{ marginLeft: "auto", fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#3a5a3a" }}>ChronoScan v2.1</span>
                    </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    <div style={{ padding: 16, border: "1px solid #0d1a0d", borderRadius: 10, background: "#060e06" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 10, textTransform: "uppercase" }}>Slice Navigator</div>
                        <input type="range" min={1} max={80} value={slice} onChange={e => setSlice(+e.target.value)} style={{ width: "100%", accentColor: "#00ff88" }} />
                        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a" }}>1</span>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#00ff88", fontWeight: 600 }}>Slice {slice}</span>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a" }}>80</span>
                        </div>
                    </div>
                    <div style={{ padding: 16, border: "1px solid #0d1a0d", borderRadius: 10, background: "#060e06" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 10, textTransform: "uppercase" }}>HU Windowing</div>
                        {windows.map(w => (
                            <div key={w.id} onClick={() => setWindow(w.id)} style={{ padding: "9px 12px", borderRadius: 6, marginBottom: 6, border: `1px solid ${window_ === w.id ? "#00ff8844" : "#0d1a0d"}`, background: window_ === w.id ? "rgba(0,255,136,0.07)" : "transparent", cursor: "pointer" }}>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: window_ === w.id ? "#00ff88" : "#3a5a3a" }}>{w.label}</div>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#1a2a1a", marginTop: 2 }}>{w.hu}</div>
                            </div>
                        ))}
                    </div>
                    <div style={{ padding: 16, border: "1px solid #0d1a0d", borderRadius: 10, background: "#060e06" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 10, textTransform: "uppercase" }}>AI Overlay</div>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#4a7a4a" }}>Grad-CAM Heatmap</span>
                            <div onClick={() => setOverlay(!overlay)} style={{ width: 40, height: 22, borderRadius: 11, border: `1px solid ${overlay ? "#00ff8844" : "#0d1a0d"}`, background: overlay ? "rgba(0,255,136,0.2)" : "#060e06", cursor: "pointer", position: "relative" }}>
                                <div style={{ position: "absolute", top: 2, left: overlay ? 20 : 2, width: 16, height: 16, borderRadius: "50%", background: overlay ? "#00ff88" : "#1a2a1a", transition: "all 0.3s" }} />
                            </div>
                        </div>
                    </div>
                    <div style={{ padding: 16, border: "1px solid #ff444444", borderRadius: 10, background: "rgba(255,68,68,0.04)" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#ff444488", marginBottom: 8, textTransform: "uppercase" }}>AI Finding</div>
                        <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 13, color: "#ff4444", marginBottom: 4 }}>{finding}</div>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#5a3a3a", lineHeight: 1.7 }}>
                            Diameter: ~14.3mm<br />Location: RUL · Slice {slice}<br />
                            LungRADS: <span style={{ color: "#ff4444" }}>4B</span> · Biopsy advised<br />
                            Confidence: <span style={{ color: "#ff4444" }}>{conf}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
