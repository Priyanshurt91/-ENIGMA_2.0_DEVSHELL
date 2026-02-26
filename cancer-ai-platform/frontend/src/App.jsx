import { useState } from "react";
import { ScanLine, GridBg, FlowChart } from "./components/Shared.jsx";
import HomeScreen from "./pages/HomeScreen.jsx";
import AnalyzeScreen from "./pages/AnalyzeScreen.jsx";
import NiftiViewer from "./pages/NiftiViewer.jsx";
import ResultCard from "./pages/ResultCard.jsx";

const GLOBAL_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #020810; overflow-x: hidden; }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #020810; }
  ::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 2px; }
  @keyframes scanline { 0% { top: -2px; } 100% { top: 100vh; } }
  @keyframes pulse-ring { 0% { transform: scale(0.8); opacity: 1; } 100% { transform: scale(2.2); opacity: 0; } }
  @keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes pageIn { from { opacity: 0; transform: scale(0.97) translateY(16px); } to { opacity: 1; transform: scale(1) translateY(0); } }
  @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-8px); } }
  @keyframes breathe { 0%, 100% { opacity: 0.25; } 50% { opacity: 0.8; } }
  @keyframes barFill { from { width: 0%; } }
  @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  @keyframes gradShift { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
  @keyframes nodeGlow { 0%, 100% { box-shadow: 0 0 12px rgba(0,255,136,0.3); } 50% { box-shadow: 0 0 28px rgba(0,255,136,0.7), 0 0 60px rgba(0,255,136,0.2); } }
  .page-enter { animation: pageIn 0.55s cubic-bezier(0.22,1,0.36,1) both; }
`;

export default function App() {
    const [page, setPage] = useState("home");
    const [analysisResult, setAnalysisResult] = useState(null);

    function navigate(to) {
        setPage(to);
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    return (
        <>
            <style>{GLOBAL_CSS}</style>
            <div style={{ background: "#020810", minHeight: "100vh", position: "relative" }}>
                <ScanLine />
                <GridBg />
                <div style={{ position: "fixed", top: "10%", left: "10%", width: 500, height: 500, background: "radial-gradient(ellipse, rgba(0,255,136,0.04) 0%, transparent 70%)", pointerEvents: "none", zIndex: 0 }} />
                <div style={{ position: "fixed", bottom: "20%", right: "5%", width: 400, height: 400, background: "radial-gradient(ellipse, rgba(0,180,255,0.04) 0%, transparent 70%)", pointerEvents: "none", zIndex: 0 }} />

                {page === "home" && <HomeScreen onNext={() => navigate("analyze")} />}
                {page === "analyze" && <AnalyzeScreen onNavigate={navigate} onAnalysisComplete={(data) => setAnalysisResult(data)} />}
                {page === "nifti" && <NiftiViewer onNavigate={navigate} analysisResult={analysisResult} />}
                {page === "result" && <ResultCard onNavigate={navigate} analysisResult={analysisResult} />}

                <FlowChart currentPage={page} onNavigate={navigate} />
            </div>
        </>
    );
}
