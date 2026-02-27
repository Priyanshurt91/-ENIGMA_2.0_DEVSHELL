import { useState, useEffect } from "react";
import { Badge } from "../components/Shared.jsx";
import { getRecentPredictions, getDashboardStats } from "../api/reportApi.js";

export default function HomeScreen({ onNext }) {
    const [hovered, setHovered] = useState(null);
    const [patients, setPatients] = useState([]);
    const [stats, setStats] = useState(null);

    const defaultStats = [
        { val: "97.3%", label: "AI Accuracy", color: "#00ff88" },
        { val: "6", label: "Cancer Types", color: "#00b4ff" },
        { val: "216K+", label: "Training Scans", color: "#c084fc" },
        { val: "Early", label: "Stage Detection", color: "#ffd93d" },
    ];

    const defaultPatients = [
        { id: "PT-0041", name: "Ananya Sharma", age: 54, risk: 91, type: "Lung", status: "CRITICAL", color: "#ff4444" },
        { id: "PT-0038", name: "Rajan Mehta", age: 61, risk: 74, type: "Brain", status: "HIGH", color: "#ff8c00" },
        { id: "PT-0035", name: "Priya Nair", age: 47, risk: 48, type: "Breast", status: "MODERATE", color: "#ffd93d" },
        { id: "PT-0029", name: "Suresh Kumar", age: 38, risk: 22, type: "Blood", status: "LOW", color: "#00ff88" },
    ];

    const riskColor = (level) => {
        const map = { CRITICAL: "#ff4444", HIGH: "#ff8c00", MODERATE: "#ffd93d", LOW: "#00ff88" };
        return map[level] || "#00ff88";
    };

    useEffect(() => {
        getRecentPredictions(10).then(res => {
            if (res.data && res.data.length > 0) {
                setPatients(res.data.map(p => ({
                    id: p.patient_id || `PT-${p.id}`,
                    name: p.patient_name || "Unknown",
                    age: p.patient_age || 0,
                    risk: Math.round(p.risk_score),
                    type: p.cancer_type?.charAt(0).toUpperCase() + p.cancer_type?.slice(1),
                    status: p.risk_level,
                    color: riskColor(p.risk_level),
                })));
            }
        }).catch(() => { });
        getDashboardStats().then(res => { if (res.data) setStats(res.data); }).catch(() => { });
    }, []);

    const displayPatients = patients.length > 0 ? patients : defaultPatients;
    const displayStats = stats ? [
        { val: `${stats.avg_confidence || 97.3}%`, label: "AI Accuracy", color: "#00ff88" },
        { val: "6", label: "Cancer Types", color: "#00b4ff" },
        { val: `${stats.total_scans || "216K+"}`, label: stats.total_scans ? "Total Scans" : "Training Scans", color: "#c084fc" },
        { val: "Early", label: "Stage Detection", color: "#ffd93d" },
    ] : defaultStats;

    return (
        <div className="page-enter" style={{ minHeight: "100vh", padding: "40px 48px 160px", position: "relative", zIndex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 52 }}>
                <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                        <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #00ff88, #00b4ff)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                            <span style={{ fontSize: 16 }}>◎</span>
                        </div>
                        <span style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: 18, color: "#e6edf3", letterSpacing: "-0.02em" }}>CancerPre</span>
                        <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a4a3a", letterSpacing: "0.1em" }}>v2.1</span>
                    </div>
                    <p style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", letterSpacing: "0.08em" }}>EARLY CANCER DETECTION SYSTEM · AI-POWERED MEDICAL IMAGING</p>
                </div>
                <div style={{ display: "flex", gap: 10 }}>
                    <Badge color="#00ff88" pulse>System Online</Badge>
                    <Badge color="#00b4ff">6 Models Active</Badge>
                </div>
            </div>

            <div style={{ marginBottom: 48, animation: "fadeUp 0.7s ease both" }}>
                <div style={{ marginBottom: 16 }}><Badge color="#00ff88" pulse>AI-Powered Early Detection</Badge></div>
                <h1 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: "clamp(36px, 5vw, 64px)", lineHeight: 1.02, letterSpacing: "-0.03em", color: "#e6edf3", marginBottom: 16 }}>
                    Detect Cancer<br />
                    <span style={{ backgroundImage: "linear-gradient(90deg, #00ff88, #00b4ff, #c084fc)", backgroundClip: "text", WebkitBackgroundClip: "text", color: "transparent", backgroundSize: "200% 200%", animation: "gradShift 4s ease infinite" }}>Before It's Too Late.</span>
                </h1>
                <p style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 300, fontSize: 15, color: "#5a7a5a", maxWidth: 480, lineHeight: 1.8 }}>AI analysis of medical imaging, blood biomarkers, and patient history — predicting cancer risk at the earliest detectable stage.</p>
            </div>

            <div style={{ display: "flex", gap: 16, marginBottom: 40, flexWrap: "wrap", animation: "fadeUp 0.7s 0.1s ease both" }}>
                {displayStats.map(s => (
                    <div key={s.label} style={{ flex: 1, minWidth: 120, padding: "18px 20px", border: `1px solid ${s.color}22`, borderRadius: 8, background: `${s.color}07` }}>
                        <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: 26, color: s.color, letterSpacing: "-1px", lineHeight: 1 }}>{s.val}</div>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginTop: 6, textTransform: "uppercase", letterSpacing: "0.08em" }}>{s.label}</div>
                    </div>
                ))}
            </div>

            <div style={{ animation: "fadeUp 0.7s 0.2s ease both" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                    <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, color: "#e6edf3" }}>Risk Worklist</div>
                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a" }}>{displayPatients.length} PATIENTS · SORTED BY RISK</div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 32 }}>
                    {displayPatients.map((p, i) => (
                        <div key={p.id + i} onMouseEnter={() => setHovered(i)} onMouseLeave={() => setHovered(null)} onClick={onNext}
                            style={{
                                display: "flex", alignItems: "center", gap: 16, padding: "14px 18px",
                                border: `1px solid ${hovered === i ? p.color + "44" : "#0d1a0d"}`,
                                borderRadius: 8, background: hovered === i ? `${p.color}07` : "#060e06",
                                cursor: "pointer", transition: "all 0.25s", transform: hovered === i ? "translateX(4px)" : "none",
                                animation: `fadeUp 0.5s ${i * 0.07}s ease both`,
                            }}>
                            <div style={{ width: 3, height: 36, borderRadius: 2, background: p.color, flexShrink: 0 }} />
                            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", width: 72 }}>{p.id}</div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 500, fontSize: 13, color: "#c8d8c8" }}>{p.name}</div>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginTop: 2 }}>Age {p.age} · {p.type} Cancer Risk</div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 18, color: p.color, lineHeight: 1 }}>{p.risk}%</div>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: p.color + "88", marginTop: 2 }}>{p.status}</div>
                            </div>
                            <div style={{ width: 60 }}>
                                <div style={{ height: 3, background: "#0d1a0d", borderRadius: 2, overflow: "hidden" }}>
                                    <div style={{ height: "100%", width: `${p.risk}%`, background: p.color, borderRadius: 2 }} />
                                </div>
                            </div>
                            <svg width="14" height="14" viewBox="0 0 14 14" style={{ opacity: hovered === i ? 0.8 : 0.2, transition: "opacity 0.3s" }}>
                                <path d="M3 7h8M8 4l3 3-3 3" stroke={p.color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </div>
                    ))}
                </div>

                <button onClick={onNext} style={{
                    display: "flex", alignItems: "center", gap: 12, padding: "16px 28px",
                    background: "linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,180,255,0.08))",
                    border: "1px solid #00ff8844", borderRadius: 8, cursor: "pointer",
                    fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14, color: "#00ff88", letterSpacing: "0.02em",
                }}
                    onMouseEnter={e => { e.target.style.background = "linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,180,255,0.12))"; e.target.style.boxShadow = "0 0 28px rgba(0,255,136,0.2)"; }}
                    onMouseLeave={e => { e.target.style.background = "linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,180,255,0.08))"; e.target.style.boxShadow = "none"; }}
                >
                    <span>→</span> Open Analyze Screen
                    <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#00ff8877", fontWeight: 400 }}>Upload & Analyze Scan</span>
                </button>
            </div>
        </div>
    );
}
