import api from "./axios";

/**
 * Upload a medical image and run AI analysis.
 * @param {File} file - Image file
 * @param {string} cancerType - lung, brain, bone, skin, breast
 * @param {string} scanType - ct, mri, xray
 * @param {Object} patientInfo - {patient_id, patient_name, patient_age}
 */
export const analyzeRadiology = (file, cancerType, scanType, patientInfo = {}) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("cancer_type", cancerType);
    formData.append("scan_type", scanType);
    if (patientInfo.patient_id) formData.append("patient_id", patientInfo.patient_id);
    if (patientInfo.patient_name) formData.append("patient_name", patientInfo.patient_name);
    if (patientInfo.patient_age) formData.append("patient_age", patientInfo.patient_age);

    return api.post("/radiology/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
};

export const getRadiologyHistory = () => api.get("/radiology/history");
