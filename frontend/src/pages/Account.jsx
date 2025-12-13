// src/pages/Account.jsx
import { useEffect, useState } from "react";
import { apiGet } from "../utils/api";
import { getEmail, getRole, clearAuth } from "../utils/auth";
import { useNavigate } from "react-router-dom";
import "../styles/Auth.css";

export default function Account() {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    const email = getEmail();
    const role = getRole();

    async function loadAccount() {
        const res = await apiGet(`/api/account?email=${email}`);

        if (res.status === 200) {
            setUser(res.data);
        }
    }

    useEffect(() => {
        loadAccount();
    }, []);

    function logout() {
        clearAuth();
        navigate("/login");
    }

    return (
        <div className="auth-container">
            <div className="auth-box glass-card" style={{ maxWidth: "480px" }}>
                <h1 className="logo-text">My Account</h1>

                {!user && <p className="text-gray-400 mt-3">Loading...</p>}

                {user && (
                    <div className="mt-4 text-left">

                        <p className="info-label">Email</p>
                        <p className="info-value">{user.email}</p>

                        <p className="info-label mt-4">Role</p>
                        <p className="info-value capitalize">{user.role}</p>

                        {user.created_at && (
                            <>
                                <p className="info-label mt-4">Joined On</p>
                                <p className="info-value">
                                    {new Date(user.created_at).toLocaleString()}
                                </p>
                            </>
                        )}
                    </div>
                )}

                <button className="auth-btn mt-6" onClick={logout}>
                    Logout
                </button>
            </div>
        </div>
    );
}
