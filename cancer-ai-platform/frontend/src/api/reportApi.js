import api from "./axios";

export const generateReport = (predictionId) => api.post(`/reports/generate/${predictionId}`);
export const getReports = () => api.get("/reports/");
export const getReport = (id) => api.get(`/reports/${id}`);

export const getDashboardStats = () => api.get("/dashboard/stats");
export const getRecentPredictions = (limit = 10) => api.get(`/dashboard/recent?limit=${limit}`);
