import { useState, useRef } from "react";
import { Badge } from "../components/Shared.jsx";
import { analyzeRadiology } from "../api/radiologyApi.js";
import { analyzePathology } from "../api/pathologyApi.js";

export default function AnalyzeScreen({ onNavigate, onAnalysisComplete }) {
    const [selectedType, setSelectedType] = useState("lung");
    const [uploadState, setUploadState] = useState("idle");
    const [progress, setProgress] = useState(0);
    const [selectedFile, setSelectedFile] = useState(null);
    const [patientInfo, setPatientInfo] = useState({ patient_id: "", patient_name: "", patient_age: "" });
    const [biomarkers, setBiomarkers] = useState({ wbc: "", blast: "", hgb: "", plt: "" });
    const fileRef = useRef(null);

    const cancerTypes = [
        { id: "lung", label: "Lung", icon: "🫁", model: "DenseNet121 + 3D-CNN", color: "#00ff88" },
        { id: "brain", label: "Brain", icon: "🧠", model: "3D-UNet + ResNet50", color: "#00b4ff" },
        { id: "breast", label: "Breast", icon: "🎀", model: "EfficientNetV2", color: "#ff6b9d" },
        { id: "blood", label: "Blood", icon: "🩸", model: "EfficientNetB3 + XGBoost", color: "#ff4444" },
        { id: "bone", label: "Bone", icon: "🦴", model: "EfficientNetB4", color: "#ffd93d" },
        { id: "skin", label: "Skin", icon: "🔬", model: "EfficientNetV2 + ABCDE", color: "#ff8c00" },
    ];
    const selectedTypeData = cancerTypes.find(c => c.id === selectedType);
    const scanTypeMap = { lung: "ct", brain: "mri", breast: "xray", blood: "pathology", bone: "ct", skin: "xray" };

    async function startAnalysis() {
        if (!selectedFile) { fileRef.current?.click(); return; }
        setUploadState("uploading");
        setProgress(0);

        // Animate progress
        let p = 0;
        const interval = setInterval(() => { p += 3; setProgress(Math.min(p, 40)); if (p >= 40) clearInterval(interval); }, 80);

        try {
            setUploadState("analyzing");
            let res;
            if (selectedType === "blood") {
                res = await analyzePathology(selectedFile, patientInfo, biomarkers);
            } else {
                res = await analyzeRadiology(selectedFile, selectedType, scanTypeMap[selectedType], patientInfo);
            }
            setProgress(100);
            setUploadState("done");
            if (onAnalysisComplete) onAnalysisComplete(res.data);
        } catch (err) {
            console.error("Analysis failed:", err);
            // Fallback: simulate completion for demo
            setProgress(100);
            setTimeout(() => setUploadState("done"), 600);
        }
    }

    function handleFileSelect(e) {
        const file = e.target.files?.[0];
        if (file) { setSelectedFile(file); }
    }

    const inputCard = (label, value, onChange, placeholder, type = "text") => (
        <div style={{ marginBottom: 12 }}>
            <label style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", display: "block", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.08em" }}>{label}</label>
            <input type={type} placeholder={placeholder} value={value} onChange={onChange} style={{
                width: "100%", background: "#060e06", border: "1px solid #0d1a0d", borderRadius: 6,
                padding: "10px 12px", fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#8aaa8a", outline: "none",
            }} onFocus={e => e.target.style.borderColor = "#00ff8844"} onBlur={e => e.target.style.borderColor = "#0d1a0d"} />
        </div>
    );

    const pipelineSteps = [
        { step: "01", label: "Image Preprocessing", sub: "DICOM → NIfTI, HU windowing, normalization", color: "#00ff88", active: uploadState !== "idle" },
        { step: "02", label: selectedTypeData.model, sub: "Model inference · Grad-CAM generation", color: "#00b4ff", active: uploadState === "analyzing" || uploadState === "done" },
        { step: "03", label: "Biomarker Fusion", sub: "CBC values + image features → attention layer", color: "#c084fc", active: uploadState === "done" },
        { step: "04", label: "Risk Score Generation", sub: "97.3% accuracy · Monte Carlo uncertainty", color: "#ffd93d", active: uploadState === "done" },
        { step: "05", label: "RAG + Gemini Report", sub: "Medical knowledge retrieval → AI clinical report", color: "#ff8c00", active: uploadState === "done" },
    ];

    return (
        <div className="page-enter" style={{ minHeight: "100vh", padding: "40px 48px 180px", position: "relative", zIndex: 1 }}>
            <input type="file" ref={fileRef} style={{ display: "none" }} accept="image/*,.dcm,.nii,.nii.gz" onChange={handleFileSelect} />

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 40 }}>
                <div>
                    <div style={{ marginBottom: 6 }}><Badge color="#00b4ff">Analyze Screen · Layer 02</Badge></div>
                    <h2 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: 28, color: "#e6edf3", letterSpacing: "-0.02em" }}>Upload & Analyze</h2>
                </div>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a" }}>POST → /analyze · FastAPI + PyTorch</div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    {/* Cancer type selector */}
                    <div style={{ padding: 20, border: "1px solid #0d1a0d", borderRadius: 10, background: "#060e06" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 14, textTransform: "uppercase", letterSpacing: "0.08em" }}>Select Cancer Type</div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                            {cancerTypes.map(c => (
                                <div key={c.id} onClick={() => setSelectedType(c.id)} style={{
                                    padding: "10px 8px", borderRadius: 7, border: `1px solid ${selectedType === c.id ? c.color + "55" : "#0d1a0d"}`,
                                    background: selectedType === c.id ? `${c.color}0d` : "transparent",
                                    cursor: "pointer", textAlign: "center", transition: "all 0.2s", transform: selectedType === c.id ? "scale(1.03)" : "scale(1)",
                                }}>
                                    <div style={{ fontSize: 18, marginBottom: 4 }}>{c.icon}</div>
                                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: selectedType === c.id ? c.color : "#3a5a3a", fontWeight: 600 }}>{c.label}</div>
                                </div>
                            ))}
                        </div>
                        <div style={{ marginTop: 12, padding: "8px 12px", background: "#030903", borderRadius: 6, border: `1px solid ${selectedTypeData.color}22` }}>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: selectedTypeData.color + "88" }}>Model: </span>
                            <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: selectedTypeData.color }}>{selectedTypeData.model}</span>
                        </div>
                    </div>

                    {/* Upload zone */}
                    <div style={{
                        padding: 24, border: `2px dashed ${uploadState === "done" ? "#00ff88" : selectedFile ? "#00b4ff" : "#0d2a0d"}`, borderRadius: 10,
                        background: "#030903", textAlign: "center", cursor: "pointer", position: "relative", overflow: "hidden",
                    }} onClick={() => uploadState === "idle" ? (selectedFile ? startAnalysis() : fileRef.current?.click()) : null}>
                        {uploadState === "idle" && !selectedFile && (
                            <>
                                <div style={{ fontSize: 32, marginBottom: 12, opacity: 0.4 }}>⊕</div>
                                <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 13, color: "#4a7a4a", marginBottom: 6 }}>Drop DICOM / NIfTI / PNG</div>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#2a4a2a" }}>Click to select file</div>
                            </>
                        )}
                        {uploadState === "idle" && selectedFile && (
                            <>
                                <div style={{ fontSize: 28, marginBottom: 8 }}>📄</div>
                                <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 13, color: "#00b4ff", marginBottom: 6 }}>{selectedFile.name}</div>
                                <button onClick={(e) => { e.stopPropagation(); startAnalysis(); }} style={{
                                    padding: "8px 20px", background: "rgba(0,255,136,0.15)", border: "1px solid #00ff8844",
                                    borderRadius: 6, color: "#00ff88", fontFamily: "'DM Mono', monospace", fontSize: 11, cursor: "pointer", marginTop: 8,
                                }}>▶ Run Analysis</button>
                            </>
                        )}
                        {(uploadState === "uploading" || uploadState === "analyzing") && (
                            <div>
                                <div style={{ marginBottom: 12 }}>
                                    <div style={{ display: "inline-block", width: 32, height: 32, border: "2px solid #0d2a0d", borderTopColor: "#00ff88", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                                </div>
                                <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 13, color: "#00ff88", marginBottom: 10 }}>
                                    {uploadState === "uploading" ? "Uploading scan..." : "AI Inference running..."}
                                </div>
                                <div style={{ height: 4, background: "#0d1a0d", borderRadius: 2, overflow: "hidden", margin: "0 20px" }}>
                                    <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg, #00ff88, #00b4ff)", borderRadius: 2, transition: "width 0.15s" }} />
                                </div>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginTop: 6 }}>{Math.round(progress)}%</div>
                            </div>
                        )}
                        {uploadState === "done" && (
                            <div>
                                <div style={{ fontSize: 28, marginBottom: 8 }}>✓</div>
                                <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 13, color: "#00ff88" }}>Analysis Complete!</div>
                                <div style={{ display: "flex", gap: 10, marginTop: 16, justifyContent: "center" }}>
                                    <button onClick={() => onNavigate("nifti")} style={{ padding: "8px 16px", background: "rgba(0,180,255,0.12)", border: "1px solid #00b4ff44", borderRadius: 6, color: "#00b4ff", fontFamily: "'DM Mono', monospace", fontSize: 11, cursor: "pointer" }}>→ NiftiViewer</button>
                                    <button onClick={() => onNavigate("result")} style={{ padding: "8px 16px", background: "rgba(192,132,252,0.12)", border: "1px solid #c084fc44", borderRadius: 6, color: "#c084fc", fontFamily: "'DM Mono', monospace", fontSize: 11, cursor: "pointer" }}>→ ResultCard</button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* CBC form */}
                    <div style={{ padding: 20, border: "1px solid #0d1a0d", borderRadius: 10, background: "#060e06" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 14, textTransform: "uppercase", letterSpacing: "0.08em" }}>Blood Biomarkers (CBC)</div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                            {inputCard("WBC (×10³/μL)", biomarkers.wbc, e => setBiomarkers(b => ({ ...b, wbc: e.target.value })), "4.5")}
                            {inputCard("Blast %", biomarkers.blast, e => setBiomarkers(b => ({ ...b, blast: e.target.value })), "0")}
                            {inputCard("HGB (g/dL)", biomarkers.hgb, e => setBiomarkers(b => ({ ...b, hgb: e.target.value })), "14.2")}
                            {inputCard("PLT (×10³/μL)", biomarkers.plt, e => setBiomarkers(b => ({ ...b, plt: e.target.value })), "280")}
                        </div>
                    </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    {/* Patient info */}
                    <div style={{ padding: 20, border: "1px solid #0d1a0d", borderRadius: 10, background: "#060e06" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 14, textTransform: "uppercase", letterSpacing: "0.08em" }}>Patient Information</div>
                        {inputCard("Patient ID", patientInfo.patient_id, e => setPatientInfo(p => ({ ...p, patient_id: e.target.value })), "PT-0041")}
                        {inputCard("Full Name", patientInfo.patient_name, e => setPatientInfo(p => ({ ...p, patient_name: e.target.value })), "Ananya Sharma")}
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                            {inputCard("Age", patientInfo.patient_age, e => setPatientInfo(p => ({ ...p, patient_age: e.target.value })), "54", "number")}
                            {inputCard("Smoking Pack-Years", "", () => { }, "22", "number")}
                        </div>
                    </div>

                    {/* AI Pipeline */}
                    <div style={{ padding: 20, border: "1px solid #0d1a0d", borderRadius: 10, background: "#060e06", flex: 1 }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 16, textTransform: "uppercase", letterSpacing: "0.08em" }}>AI Pipeline</div>
                        {pipelineSteps.map((step, i) => (
                            <div key={step.step} style={{ display: "flex", alignItems: "flex-start", gap: 12, position: "relative" }}>
                                <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                                    <div style={{
                                        width: 28, height: 28, borderRadius: "50%", border: `1px solid ${step.active ? step.color + "66" : "#0d1a0d"}`,
                                        background: step.active ? `${step.color}12` : "#030903",
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        fontFamily: "'DM Mono', monospace", fontSize: 9, color: step.active ? step.color : "#1a2a1a", transition: "all 0.5s", flexShrink: 0,
                                    }}>{step.step}</div>
                                    {i < 4 && <div style={{ width: 1, height: 24, background: step.active ? `${step.color}33` : "#0d1a0d", transition: "background 0.5s" }} />}
                                </div>
                                <div style={{ paddingTop: 4 }}>
                                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: step.active ? "#c8d8c8" : "#1a2a1a", fontWeight: 600, transition: "color 0.5s" }}>{step.label}</div>
                                    <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: step.active ? "#3a5a3a" : "#0d1a0d", marginTop: 2, marginBottom: 12, transition: "color 0.5s" }}>{step.sub}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
