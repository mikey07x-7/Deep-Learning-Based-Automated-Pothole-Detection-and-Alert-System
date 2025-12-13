// src/utils/auth.js

// Save auth data after login/register
export function saveAuth(email, role, token) {
    localStorage.setItem("rs_email", email);
    localStorage.setItem("rs_role", role);
    localStorage.setItem("rs_token", token);
}

// Check if user is logged in
export function isLoggedIn() {
    return localStorage.getItem("rs_email") !== null &&
           localStorage.getItem("rs_token") !== null;
}

// Get email
export function getEmail() {
    return localStorage.getItem("rs_email");
}

// Get role: citizen / authority
export function getRole() {
    return localStorage.getItem("rs_role");
}

// Get token for authorized API calls
export function getToken() {
    return localStorage.getItem("rs_token");
}

// Logout
export function clearAuth() {
    localStorage.removeItem("rs_email");
    localStorage.removeItem("rs_role");
    localStorage.removeItem("rs_token");
}
