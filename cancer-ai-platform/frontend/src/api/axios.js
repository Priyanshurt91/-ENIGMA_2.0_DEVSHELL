import axios from "axios";

const api = axios.create({
    baseURL: process.env.NODE_ENV === "production" ? "/api/v1" : "http://localhost:8000/api/v1",
    timeout: 60000, // 60 second timeout — prevents UI hanging forever if backend is slow
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("chronoscan_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
