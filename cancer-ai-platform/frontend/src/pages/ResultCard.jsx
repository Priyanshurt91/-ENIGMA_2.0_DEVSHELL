import { useState, useEffect } from "react";
import { Badge } from "../components/Shared.jsx";
import { generateReport } from "../api/reportApi.js";

function _getRecommendations(cancerType, riskLevel, pClass) {
    const isCritical = riskLevel === "CRITICAL" || riskLevel === "HIGH";
    const recs = {
        lung: [
            { icon: "⚡", title: "Recommended Action", desc: isCritical ? "Schedule PET-CT scan within 7 days. Refer to thoracic oncologist. Consider CT-guided biopsy." : "Follow-up low-dose CT in 6 months. Monitor for symptom changes.", color: "#ff4444" },
            { icon: "💊", title: "Treatment Pathway", desc: isCritical ? "Staging workup required. Lobectomy + adjuvant chemotherapy may be indicated. Pembrolizumab if PD-L1 > 50%." : "Continue routine LDCT screening. Annual follow-up as per guidelines.", color: "#ff8c00" },
            { icon: "📊", title: "Prognosis Estimate", desc: isCritical ? "5-year survival depends on staging. Early-stage: 68-92%. Molecular profiling recommended for targeted therapy." : "Low-risk findings. 5-year survival >90% with surveillance.", color: "#c084fc" },
            { icon: "🔄", title: "ChronoScan Follow-up", desc: isCritical ? "Serial imaging recommended to assess volume doubling time. RECIST criteria for response monitoring." : "Re-scan in 6-12 months. Track nodule size and morphology.", color: "#00b4ff" },
        ],
        brain: [
            { icon: "⚡", title: "Recommended Action", desc: isCritical ? "Urgent neurosurgical consultation. MRI with contrast. Consider stereotactic biopsy." : "Follow-up MRI in 3-6 months with contrast.", color: "#ff4444" },
            { icon: "💊", title: "Treatment Pathway", desc: isCritical ? "Maximal safe resection + Stupp protocol (temozolomide + radiation). Check IDH/MGMT status." : "Observation with serial MRI. Monitor for growth or symptom progression.", color: "#ff8c00" },
            { icon: "📊", title: "Molecular Profile", desc: isCritical ? "IDH mutation and MGMT methylation testing recommended. 1p/19q codeletion for oligodendroglioma." : "Low-grade features. Consider watchful waiting with serial imaging.", color: "#c084fc" },
            { icon: "🔄", title: "ChronoScan Follow-up", desc: "Serial volumetric MRI for growth assessment. Perfusion MRI to evaluate vascularity.", color: "#00b4ff" },
        ],
        breast: [
            { icon: "⚡", title: "Recommended Action", desc: isCritical ? "Core needle biopsy recommended. Breast MRI for extent assessment. Refer to breast surgeon." : "Short-interval follow-up mammography in 6 months.", color: "#ff4444" },
            { icon: "💊", title: "Treatment Pathway", desc: isCritical ? "Hormonal receptor, HER2, Ki-67 testing. Lumpectomy vs mastectomy. Consider neoadjuvant therapy." : "Continue routine screening per guidelines. Annual mammography.", color: "#ff8c00" },
            { icon: "📊", title: "Risk Assessment", desc: isCritical ? "BI-RADS classification suggests high suspicion. Genetic counseling for BRCA testing if family history." : "Low suspicion lesion. Likely benign features.", color: "#c084fc" },
            { icon: "🔄", title: "ChronoScan Follow-up", desc: "Track morphology changes. Comparative imaging for interval assessment.", color: "#00b4ff" },
        ],
        blood: [
            { icon: "⚡", title: "Recommended Action", desc: isCritical ? "Urgent hematology referral. Bone marrow biopsy. Flow cytometry analysis." : "Repeat CBC with differential in 2-4 weeks. Monitor blast percentage.", color: "#ff4444" },
            { icon: "💊", title: "Treatment Pathway", desc: isCritical ? "Induction chemotherapy based on subtype. ALL: multi-agent protocol. AML: 7+3 regimen. CML: TKI therapy." : "Monitor with serial CBC. Watch for cytopenias or rising blast count.", color: "#ff8c00" },
            { icon: "📊", title: "Lab Correlation", desc: isCritical ? "Cytogenetic analysis for risk stratification. MRD assessment for treatment monitoring." : "Current values within acceptable range. Continue monitoring.", color: "#c084fc" },
            { icon: "🔄", title: "ChronoScan Follow-up", desc: "Serial peripheral smear analysis. Track blast percentage trend over time.", color: "#00b4ff" },
        ],
        bone: [
            { icon: "⚡", title: "Recommended Action", desc: isCritical ? "Orthopedic oncology referral. MRI for soft-tissue extent. Consider CT-guided biopsy." : "Follow-up imaging in 3-6 months. Monitor for growth.", color: "#ff4444" },
            { icon: "💊", title: "Treatment Pathway", desc: isCritical ? "Staging workup including bone scan and chest CT. Neoadjuvant chemotherapy if high-grade." : "Observation with serial imaging. Low suspicion for malignancy.", color: "#ff8c00" },
            { icon: "📊", title: "Classification", desc: isCritical ? "Lodwick classification suggests aggressive lesion. Histological confirmation required." : "Lodwick IA pattern. Slow-growing, likely benign features.", color: "#c084fc" },
            { icon: "🔄", title: "ChronoScan Follow-up", desc: "Serial imaging for growth assessment. Track margin characteristics.", color: "#00b4ff" },
        ],
        skin: [
            { icon: "⚡", title: "Recommended Action", desc: isCritical ? "Dermatology referral for dermoscopic evaluation. Excisional biopsy recommended." : "Monitor lesion with serial dermoscopy. Photo documentation.", color: "#ff4444" },
            { icon: "💊", title: "Treatment Pathway", desc: isCritical ? "Wide local excision with margins. Sentinel lymph node biopsy if >1mm depth. Immunotherapy if advanced." : "Observation. Re-evaluate in 3-6 months.", color: "#ff8c00" },
            { icon: "📊", title: "ABCDE Assessment", desc: isCritical ? "Asymmetry, border irregularity, color variation, diameter >6mm, evolution noted." : "Features within normal limits. Low suspicion by ABCDE criteria.", color: "#c084fc" },
            { icon: "🔄", title: "ChronoScan Follow-up", desc: "Serial imaging for morphological change. Full-body skin screening recommended.", color: "#00b4ff" },
        ],
    };
    return recs[cancerType] || recs.lung;
}

export default function ResultCard({ onNavigate, analysisResult }) {
    const [tab, setTab] = useState("risk");
    const [report, setReport] = useState(null);
    const [loadingReport, setLoadingReport] = useState(false);
    const r = analysisResult || {};
    const riskScore = r.risk_score || 91;
    const riskLevel = r.risk_level || "CRITICAL";
    const pClass = r.predicted_class || "malignant";
    const conf = r.confidence || 91;
    const pName = r.patient_name || "Ananya Sharma";
    const pId = r.patient_id || "PT-0041";
    const pAge = r.patient_age || 54;

    const probs = r.probabilities || {};
    const cancerType = r.cancer_type || "lung";
    const cancerLabel = { lung: "Lung Cancer", brain: "Brain Tumor", breast: "Breast Cancer", blood: "Blood Cancer", bone: "Bone Cancer", skin: "Skin Cancer" }[cancerType] || "Cancer";
    const cancerColor = { lung: "#ff4444", brain: "#00b4ff", breast: "#ff6b9d", blood: "#ff6b6b", bone: "#ffd93d", skin: "#ff8c00" }[cancerType] || "#ff4444";
    const gradeMap = {
        lung: riskScore > 70 ? "LungRADS 4B" : riskScore > 40 ? "LungRADS 4A" : "LungRADS 3",
        brain: riskScore > 70 ? "WHO Grade III-IV" : riskScore > 40 ? "WHO Grade II" : "WHO Grade I",
        breast: riskScore > 70 ? "BI-RADS 5" : riskScore > 40 ? "BI-RADS 4" : "BI-RADS 3",
        blood: riskScore > 70 ? "Blast >20%" : riskScore > 40 ? "Blast 5-20%" : "Blast <5%",
        bone: riskScore > 70 ? "Lodwick III" : riskScore > 40 ? "Lodwick II" : "Lodwick IA",
        skin: riskScore > 70 ? "ABCDE High" : riskScore > 40 ? "ABCDE Moderate" : "ABCDE Low",
    };
    const modelScores = [
        { name: cancerLabel, score: riskScore, color: cancerColor, grade: gradeMap[cancerType] || "N/A" },
    ];
    const tabs = [
        { id: "risk", label: "Risk Dashboard" },
        { id: "report", label: "Clinical Report" }
    ];

    useEffect(() => {
        if (tab === "report" && !report && r.id) {
            setLoadingReport(true);
            generateReport(r.id).then(res => { setReport(res.data); setLoadingReport(false); })
                .catch(() => setLoadingReport(false));
        }
    }, [tab, r.id]);

    const defaultSections = [
        { label: "CLINICAL INDICATION", text: `${pAge}-year-old presenting for ${r.cancer_type || "lung"} cancer screening. AI-assisted analysis requested.` },
        { label: "TECHNIQUE", text: `AI inference: ${r.cancer_type || "Lung"} cancer model. Grad-CAM heatmap overlay applied.` },
        { label: "FINDINGS", text: `${pClass !== "normal" ? pClass : "No abnormalities"} detected with ${conf}% confidence. Risk score: ${riskScore}%.` },
        { label: "IMPRESSION", text: `${pClass !== "normal" ? pClass : "Normal scan"}. Risk Level: ${riskLevel}. ${riskLevel === "CRITICAL" ? "Clinical correlation recommended." : "Routine follow-up."}` },
        { label: "RECOMMENDATION", text: riskLevel === "CRITICAL" ? `1. Specialist referral. 2. Additional imaging. 3. Consider biopsy. 4. Molecular profiling if confirmed.` : "Routine screening." },
    ];

    const reportSections = report?.sections
        ? Object.entries(report.sections).map(([key, text]) => ({ label: key.toUpperCase().replace(/_/g, " "), text }))
        : defaultSections;

    return (
        <div className="page-enter" style={{ minHeight: "100vh", padding: "40px 48px 180px", position: "relative", zIndex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
                <div>
                    <div style={{ marginBottom: 6 }}><Badge color="#c084fc">ResultCard · Clinical Deliverables</Badge></div>
                    <h2 style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: 28, color: "#e6edf3" }}>Patient Risk Report</h2>
                </div>
                <div style={{ display: "flex", gap: 10 }}>
                    <button onClick={() => onNavigate("nifti")} style={{ padding: "9px 18px", background: "rgba(0,180,255,0.1)", border: "1px solid #00b4ff33", borderRadius: 7, color: "#00b4ff", fontFamily: "'DM Mono', monospace", fontSize: 11, cursor: "pointer" }}>← NiftiViewer</button>
                    <button style={{ padding: "9px 18px", background: "rgba(0,255,136,0.1)", border: "1px solid #00ff8833", borderRadius: 7, color: "#00ff88", fontFamily: "'DM Mono', monospace", fontSize: 11, cursor: "pointer" }}>⬇ Export PDF</button>
                </div>
            </div>

            <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: "1px solid #0d1a0d" }}>
                {tabs.map(t => (
                    <div key={t.id} onClick={() => setTab(t.id)} style={{ padding: "8px 16px", cursor: "pointer", fontFamily: "'DM Mono', monospace", fontSize: 11, color: tab === t.id ? "#00ff88" : "#3a5a3a", borderBottom: `2px solid ${tab === t.id ? "#00ff88" : "transparent"}`, marginBottom: -1 }}>{t.label}</div>
                ))}
            </div>

            {tab === "risk" && (
                <div style={{ animation: "fadeUp 0.4s ease both" }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 20, marginBottom: 20 }}>
                        <div style={{ padding: 28, border: "1px solid #ff444444", borderRadius: 12, background: "rgba(255,68,68,0.04)", textAlign: "center" }}>
                            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#ff444488", marginBottom: 8, textTransform: "uppercase" }}>Overall Risk Score</div>
                            <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: 72, color: "#ff4444", lineHeight: 1, textShadow: "0 0 40px rgba(255,68,68,0.4)", letterSpacing: "-3px" }}>{Math.round(riskScore)}<span style={{ fontSize: 28 }}>%</span></div>
                            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#ff4444", marginTop: 8, padding: "4px 12px", border: "1px solid #ff444444", display: "inline-block", borderRadius: 4 }}>{riskLevel} · IMMEDIATE ACTION</div>
                            <div style={{ marginTop: 16 }}>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a" }}>{pId} · {pName} · Age {pAge}</div>
                            </div>
                        </div>
                        <div style={{ padding: 24, border: "1px solid #0d1a0d", borderRadius: 12, background: "#060e06" }}>
                            <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 16, textTransform: "uppercase" }}>Per-Cancer Risk Breakdown</div>
                            {modelScores.map((m, i) => (
                                <div key={m.name} style={{ marginBottom: 14, animation: `fadeUp 0.4s ${i * 0.08}s ease both` }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                                        <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: "#8aaa8a" }}>{m.name}</span>
                                        <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: m.color, fontWeight: 600 }}>{m.score}% · {m.grade}</span>
                                    </div>
                                    <div style={{ height: 5, background: "#0d1a0d", borderRadius: 3, overflow: "hidden" }}>
                                        <div style={{ height: "100%", width: `${m.score}%`, background: m.color, borderRadius: 3, animation: `barFill 1.2s ease both`, animationDelay: `${i * 0.1}s` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                        {_getRecommendations(cancerType, riskLevel, pClass).map(rec => (
                            <div key={rec.title} style={{ padding: "16px 18px", border: `1px solid ${rec.color}22`, borderRadius: 10, background: `${rec.color}05` }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                                    <span style={{ fontSize: 16 }}>{rec.icon}</span>
                                    <span style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 12, color: rec.color }}>{rec.title}</span>
                                </div>
                                <p style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#4a6a4a", lineHeight: 1.7 }}>{rec.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {tab === "report" && (
                <div style={{ animation: "fadeUp 0.4s ease both" }}>
                    <div style={{ padding: 28, border: "1px solid #0d1a0d", borderRadius: 12, background: "#060e06" }}>
                        <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#3a5a3a", marginBottom: 20, textTransform: "uppercase" }}>
                            {report ? `AI-Generated Report · ${report.generated_by === "gemini" ? "Gemini + RAG" : "Rule-Based + RAG"}` : loadingReport ? "Generating Report via RAG + Gemini..." : "Auto-Generated Radiology Report"}
                        </div>
                        {loadingReport && <div style={{ textAlign: "center", padding: 40 }}><div style={{ display: "inline-block", width: 32, height: 32, border: "2px solid #0d2a0d", borderTopColor: "#00ff88", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} /></div>}
                        {!loadingReport && reportSections.map(s => (
                            <div key={s.label} style={{ marginBottom: 20 }}>
                                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#00ff8877", marginBottom: 5, letterSpacing: "0.1em" }}>{s.label}</div>
                                <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: "#6a8a6a", lineHeight: 1.8, fontWeight: 300 }}>{s.text}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
