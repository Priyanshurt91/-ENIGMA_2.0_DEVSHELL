"""
Gemini Service — calls Google Gemini API to generate polished clinical reports.
"""
from app.config import settings
from app.core.logging import logger

_model = None


def initialize():
    """Initialize the Gemini API client."""
    global _model
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set. Gemini report generation disabled.")
        return

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"Gemini API initialized with model: {settings.GEMINI_MODEL}")
    except Exception as e:
        logger.error(f"Gemini initialization failed: {e}")
        _model = None


async def generate_report(
    prediction_data: dict,
    rag_context: list[str],
    patient_info: dict = None,
) -> dict | None:
    """
    Generate a polished clinical report using Gemini API.

    Args:
        prediction_data: {cancer_type, predicted_class, confidence, risk_score, probabilities}
        rag_context: list of relevant medical knowledge passages from RAG
        patient_info: {patient_id, name, age, biomarkers}

    Returns:
        dict with sections: {indication, technique, findings, impression, recommendation, executive_summary}
        or None if Gemini is unavailable
    """
    if _model is None:
        return None

    # Build the prompt
    context_text = "\n".join(f"- {ctx}" for ctx in rag_context)
    patient_text = ""
    if patient_info:
        patient_text = f"""
Patient ID: {patient_info.get('patient_id', 'N/A')}
Name: {patient_info.get('name', 'N/A')}
Age: {patient_info.get('age', 'N/A')}
"""
        if patient_info.get("biomarkers"):
            bm = patient_info["biomarkers"]
            patient_text += f"Biomarkers: WBC={bm.get('wbc','N/A')}, Blast%={bm.get('blast','N/A')}, HGB={bm.get('hgb','N/A')}, PLT={bm.get('plt','N/A')}\n"

    prompt = f"""You are a senior radiologist and oncologist AI assistant. Generate a structured clinical report based on the following AI analysis results and retrieved medical knowledge.

## AI PREDICTION RESULTS
- Cancer Type: {prediction_data.get('cancer_type', 'Unknown')}
- Scan Type: {prediction_data.get('scan_type', 'Unknown')}
- Predicted Class: {prediction_data.get('predicted_class', 'Unknown')}
- Confidence: {prediction_data.get('confidence', 0)}%
- Risk Score: {prediction_data.get('risk_score', 0)}%
- Class Probabilities: {prediction_data.get('probabilities', {{}})}

## PATIENT INFORMATION
{patient_text if patient_text else "Not provided"}

## RELEVANT MEDICAL KNOWLEDGE (Retrieved via RAG)
{context_text}

## INSTRUCTIONS
Generate a structured radiology/pathology report with these exact sections in JSON format:
1. "executive_summary" - 2-3 sentence high-level summary of findings and urgency
2. "indication" - Clinical indication for the study
3. "technique" - Imaging technique and AI analysis method used
4. "findings" - Detailed findings from the AI analysis with measurements and descriptions
5. "impression" - Clinical impression and diagnosis
6. "recommendation" - Specific next steps, follow-up actions, and treatment considerations
7. "risk_assessment" - Risk level classification with supporting evidence
8. "confidence_disclaimer" - Standard AI-assisted diagnosis disclaimer

Important:
- Use professional medical terminology
- Reference specific measurements, scores, and classifications
- Include evidence-based recommendations
- Add appropriate urgency indicators
- Mention both the AI confidence and the clinical significance

Return ONLY valid JSON with these section keys and string values.
"""

    try:
        response = _model.generate_content(prompt)
        text = response.text.strip()

        # Try to parse as JSON
        import json
        # Clean up markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        try:
            sections = json.loads(text)
            return sections
        except json.JSONDecodeError:
            # Return as full text if not valid JSON
            return {
                "executive_summary": text[:300],
                "indication": "AI-assisted cancer screening analysis",
                "technique": f"AI model analysis for {prediction_data.get('cancer_type', 'unknown')} cancer detection",
                "findings": text,
                "impression": f"{prediction_data.get('predicted_class', 'Unknown')} detected with {prediction_data.get('confidence', 0)}% confidence",
                "recommendation": "Please consult with a specialist for clinical correlation.",
                "risk_assessment": f"Risk Score: {prediction_data.get('risk_score', 0)}%",
                "confidence_disclaimer": "This report is AI-generated and should be reviewed by a qualified medical professional.",
            }

    except Exception as e:
        logger.error(f"Gemini report generation failed: {e}")
        return None
