import api from "./axios";

/**
 * Upload a blood slide image and run blood cancer analysis.
 * @param {File} file - Blood slide image
 * @param {Object} patientInfo - {patient_id, patient_name, patient_age}
 * @param {Object} biomarkers - {wbc, blast, hgb, plt}
 */
export const analyzePathology = (file, patientInfo = {}, biomarkers = {}) => {
    const formData = new FormData();
    formData.append("file", file);
    if (patientInfo.patient_id) formData.append("patient_id", patientInfo.patient_id);
    if (patientInfo.patient_name) formData.append("patient_name", patientInfo.patient_name);
    if (patientInfo.patient_age) formData.append("patient_age", patientInfo.patient_age);
    if (biomarkers.wbc) formData.append("wbc", biomarkers.wbc);
    if (biomarkers.blast) formData.append("blast", biomarkers.blast);
    if (biomarkers.hgb) formData.append("hgb", biomarkers.hgb);
    if (biomarkers.plt) formData.append("plt", biomarkers.plt);

    return api.post("/pathology/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
};

export const getPathologyHistory = () => api.get("/pathology/history");
