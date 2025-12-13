// src/utils/api.js

import { getToken, clearAuth } from "./auth";

const API_BASE = import.meta.env.VITE_API_BASE;

// Generic fetch wrapper
async function request(endpoint, method = "GET", body = null, isFormData = false) {
    const headers = {};

    if (!isFormData) headers["Content-Type"] = "application/json";

    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${endpoint}`, {
        method,
        headers,
        body: isFormData ? body : body ? JSON.stringify(body) : null,
    });

    // Auto logout if unauthorized
    if (res.status === 401) {
        clearAuth();
        window.location.href = "/login";
        return;
    }

    let data = null;

    try {
        data = await res.json();
    } catch (err) {
        console.warn("API returned no JSON:", endpoint);
    }

    return { status: res.status, data };
}

// Export request shortcuts
export function apiGet(endpoint) {
    return request(endpoint, "GET");
}

export function apiPost(endpoint, body) {
    return request(endpoint, "POST", body);
}

export function apiPut(endpoint, body) {
    return request(endpoint, "PUT", body);
}

export function apiDelete(endpoint) {
    return request(endpoint, "DELETE");
}

// For uploading images (Report page)
export function apiUpload(endpoint, formData) {
    return request(endpoint, "POST", formData, true);
}
