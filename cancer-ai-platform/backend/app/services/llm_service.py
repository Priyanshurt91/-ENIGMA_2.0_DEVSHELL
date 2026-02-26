"""
LLM Service — Orchestrator for RAG → Gemini pipeline.
Falls back to rule-based generation if Gemini is unavailable.
"""
from app.services import rag_service, gemini_service
from app.core.constants import risk_level_from_score
from app.core.logging import logger


async def generate_report(
    prediction_data: dict,
    patient_info: dict = None,
) -> dict:
    """
    Full pipeline: prediction → RAG context → Gemini report.
    Falls back to rule-based if Gemini unavailable.

    Returns: dict with report sections
    """
    cancer_type = prediction_data.get("cancer_type", "unknown")
    predicted_class = prediction_data.get("predicted_class", "unknown")
    confidence = prediction_data.get("confidence", 0)

    # Step 1: Retrieve context from RAG
    logger.info(f"RAG retrieval for {cancer_type}/{predicted_class}")
    rag_context = rag_service.retrieve_context(cancer_type, predicted_class, confidence)

    # Step 2: Try Gemini
    logger.info("Attempting Gemini report generation...")
    gemini_report = await gemini_service.generate_report(prediction_data, rag_context, patient_info)

    if gemini_report:
        logger.info("Gemini report generated successfully.")
        return {"sections": gemini_report, "generated_by": "gemini"}

    # Step 3: Fallback to rule-based
    logger.info("Gemini unavailable, using rule-based report generation.")
    return {"sections": _rule_based_report(prediction_data, rag_context, patient_info), "generated_by": "rule_based"}


def _rule_based_report(prediction_data: dict, rag_context: list[str], patient_info: dict = None) -> dict:
    """Generate a structured report using rules and RAG context."""
    cancer_type = prediction_data.get("cancer_type", "Unknown")
    scan_type = prediction_data.get("scan_type", "Unknown")
    predicted_class = prediction_data.get("predicted_class", "Unknown")
    confidence = prediction_data.get("confidence", 0)
    risk_score = prediction_data.get("risk_score", 0)
    risk_level = risk_level_from_score(risk_score)

    patient_desc = "Patient"
    if patient_info:
        name = patient_info.get("name", "")
        age = patient_info.get("age", "")
        patient_desc = f"{name}, age {age}" if name and age else "Patient"

    # Executive summary
    urgency = "IMMEDIATE ACTION REQUIRED" if risk_level.value == "CRITICAL" else \
              "Follow-up recommended" if risk_level.value == "HIGH" else \
              "Routine follow-up" if risk_level.value == "MODERATE" else "No immediate concern"

    executive_summary = (
        f"AI-assisted {cancer_type} cancer screening for {patient_desc}. "
        f"Analysis indicates {predicted_class} with {confidence}% confidence. "
        f"Risk Level: {risk_level.value}. {urgency}."
    )

    # Technique
    model_map = {
        "lung": "DenseNet121 + 3D-CNN",
        "brain": "3D-UNet + ResNet50",
        "blood": "EfficientNetB3 + XGBoost",
        "bone": "EfficientNetB4",
        "skin": "EfficientNetV2 + ABCDE",
        "breast": "EfficientNetV2",
    }
    model_name = model_map.get(cancer_type.lower(), "Deep Learning Model")

    technique = (
        f"{scan_type.upper()} imaging analysis using AI model: {model_name}. "
        f"Grad-CAM heatmap overlay applied for explainability. "
        f"Image preprocessed with standard normalization pipeline."
    )

    # Findings — incorporate RAG context
    findings_parts = [f"Primary finding: {predicted_class} detected with {confidence}% confidence."]
    for ctx in rag_context[:3]:
        findings_parts.append(ctx)
    findings = " ".join(findings_parts)

    # Impression
    impression = (
        f"{predicted_class.replace('_', ' ').title()} identified in {cancer_type} cancer screening. "
        f"AI confidence: {confidence}%. Overall risk score: {risk_score}% ({risk_level.value}). "
        f"Clinical correlation recommended."
    )

    # Recommendations
    if risk_level.value == "CRITICAL":
        recommendation = (
            f"1. Urgent specialist referral within 7 days. "
            f"2. Additional imaging (PET-CT/MRI) for staging. "
            f"3. Tissue biopsy for histological confirmation. "
            f"4. Molecular profiling if malignancy confirmed. "
            f"5. Multidisciplinary tumor board discussion."
        )
    elif risk_level.value == "HIGH":
        recommendation = (
            f"1. Specialist consultation within 2 weeks. "
            f"2. Follow-up imaging in 3 months. "
            f"3. Consider biopsy based on clinical assessment. "
            f"4. Monitor for symptom progression."
        )
    elif risk_level.value == "MODERATE":
        recommendation = (
            f"1. Follow-up imaging in 6 months. "
            f"2. Clinical monitoring for new symptoms. "
            f"3. Repeat screening as per guidelines."
        )
    else:
        recommendation = (
            f"1. Continue routine screening schedule. "
            f"2. Annual follow-up recommended. "
            f"3. Report any new symptoms to healthcare provider."
        )

    return {
        "executive_summary": executive_summary,
        "indication": f"{patient_desc} presenting for {cancer_type} cancer screening via {scan_type.upper()} analysis.",
        "technique": technique,
        "findings": findings,
        "impression": impression,
        "recommendation": recommendation,
        "risk_assessment": f"Risk Score: {risk_score}% | Level: {risk_level.value}",
        "confidence_disclaimer": (
            "DISCLAIMER: This report was generated by an AI system (ChronoScan v2.1) and is intended "
            "to assist clinical decision-making. It should NOT be used as the sole basis for diagnosis "
            "or treatment. All findings must be reviewed and confirmed by a qualified medical professional."
        ),
    }
