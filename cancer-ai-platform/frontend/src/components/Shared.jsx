import { useState } from "react";

export function ScanLine() {
    return (
        <div style={{
            position: "fixed", left: 0, right: 0, height: "1px", zIndex: 9999,
            background: "linear-gradient(90deg, transparent 0%, rgba(0,255,136,0.5) 50%, transparent 100%)",
            animation: "scanline 7s linear infinite", pointerEvents: "none",
        }} />
    );
}

export function GridBg() {
    return (
        <div style={{
            position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none",
            backgroundImage: "linear-gradient(rgba(0,255,136,0.018) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,136,0.018) 1px, transparent 1px)",
            backgroundSize: "44px 44px",
        }} />
    );
}

export function Dot({ color = "#00ff88", size = 8, pulse = false }) {
    return (
        <span style={{ position: "relative", display: "inline-flex", alignItems: "center", justifyContent: "center", width: size, height: size }}>
            {pulse && <span style={{
                position: "absolute", inset: 0, borderRadius: "50%", background: color,
                animation: "pulse-ring 1.8s cubic-bezier(0,0,0.2,1) infinite", opacity: 0.5,
            }} />}
            <span style={{ width: size - 2, height: size - 2, borderRadius: "50%", background: color, position: "relative" }} />
        </span>
    );
}

export function Badge({ children, color = "#00ff88", pulse = false }) {
    return (
        <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            padding: "4px 12px", border: `1px solid ${color}44`,
            background: `${color}09`, borderRadius: 3,
            fontFamily: "'DM Mono', monospace", fontSize: 10,
            color, letterSpacing: "0.12em", textTransform: "uppercase",
        }}>
            <Dot color={color} size={6} pulse={pulse} />
            {children}
        </div>
    );
}

export function FlowArrow({ active }) {
    return (
        <div style={{ display: "flex", alignItems: "center", width: 48, position: "relative" }}>
            <div style={{ flex: 1, height: 1, background: active ? "#00ff88" : "#1e2d1e", transition: "background 0.5s" }} />
            <svg width="8" height="8" viewBox="0 0 8 8">
                <polygon points="0,0 8,4 0,8" fill={active ? "#00ff88" : "#1e2d1e"} style={{ transition: "fill 0.5s" }} />
            </svg>
        </div>
    );
}

export function FlowChart({ currentPage, onNavigate }) {
    const nodeStyle = (id, color = "#00ff88") => {
        const active = currentPage === id;
        const visited = getVisitOrder(currentPage) > getVisitOrder(id);
        return {
            padding: "10px 18px", border: `1px solid ${active ? color : visited ? color + "55" : "#1e2d1e"}`,
            borderRadius: 6, background: active ? `${color}12` : visited ? `${color}07` : "#0a130a",
            color: active ? color : visited ? color + "bb" : "#3a4a3a",
            fontFamily: "'DM Mono', monospace", fontSize: 11, fontWeight: 600,
            cursor: "pointer", transition: "all 0.3s",
            boxShadow: active ? `0 0 18px ${color}44, inset 0 0 18px ${color}08` : "none",
            animation: active ? "nodeGlow 2.5s ease-in-out infinite" : "none",
            whiteSpace: "nowrap", letterSpacing: "0.05em",
        };
    };

    function getVisitOrder(page) {
        const order = { home: 0, analyze: 1, nifti: 2, result: 2 };
        return order[page] ?? -1;
    }

    const arrowColor = (fromId) => getVisitOrder(currentPage) > getVisitOrder(fromId) ? "#00ff88" : "#1e2d1e";

    return (
        <div style={{
            position: "fixed", bottom: 0, left: 0, right: 0, zIndex: 100,
            background: "linear-gradient(180deg, transparent 0%, #020810ee 30%, #020810 100%)",
            padding: "20px 40px 24px", borderTop: "1px solid rgba(0,255,136,0.08)",
        }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0 }}>
                <div onClick={() => onNavigate("home")} style={nodeStyle("home")}>
                    <span style={{ fontSize: 9, opacity: 0.6, display: "block", marginBottom: 2 }}>01</span>
                    <span>HomeScreen</span>
                </div>
                <FlowArrow active={getVisitOrder(currentPage) > 0} />
                <div onClick={() => onNavigate("analyze")} style={nodeStyle("analyze")}>
                    <span style={{ fontSize: 9, opacity: 0.6, display: "block", marginBottom: 2 }}>02</span>
                    <span>AnalyzeScreen</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", position: "relative", width: 80 }}>
                    <svg width="80" height="60" viewBox="0 0 80 60" style={{ overflow: "visible" }}>
                        <path d="M0,30 Q30,30 40,15 Q50,0 80,0" stroke={arrowColor("analyze")} strokeWidth="1" fill="none" strokeDasharray={getVisitOrder(currentPage) > 1 ? "none" : "4 4"} />
                        <path d="M0,30 Q30,30 40,45 Q50,60 80,60" stroke={arrowColor("analyze")} strokeWidth="1" fill="none" strokeDasharray={getVisitOrder(currentPage) > 1 ? "none" : "4 4"} />
                        {getVisitOrder(currentPage) > 1 && <>
                            <polygon points="76,0 80,0 80,4" fill={arrowColor("analyze")} />
                            <polygon points="76,56 80,60 76,64" fill={arrowColor("analyze")} />
                        </>}
                    </svg>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    <div onClick={() => onNavigate("nifti")} style={nodeStyle("nifti", "#00b4ff")}>
                        <span style={{ fontSize: 9, opacity: 0.6, display: "block", marginBottom: 2 }}>03A</span>
                        <span>NiftiViewer</span>
                    </div>
                    <div onClick={() => onNavigate("result")} style={nodeStyle("result", "#c084fc")}>
                        <span style={{ fontSize: 9, opacity: 0.6, display: "block", marginBottom: 2 }}>03B</span>
                        <span>ResultCard</span>
                    </div>
                </div>
            </div>
            <div style={{ display: "flex", justifyContent: "center", gap: 60, marginTop: 10 }}>
                {["Frontend Layer", "Backend AI Layer", "Output Layer"].map(l => (
                    <span key={l} style={{ fontFamily: "'DM Mono', monospace", fontSize: 9, color: "#2a3a2a", textTransform: "uppercase", letterSpacing: "0.1em" }}>{l}</span>
                ))}
            </div>
        </div>
    );
}
