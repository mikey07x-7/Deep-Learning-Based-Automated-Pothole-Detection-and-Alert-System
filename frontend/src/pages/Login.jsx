// src/pages/Login.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { saveAuth } from "../utils/auth";
import { apiPost } from "../utils/api";
import "../styles/Auth.css";

export default function Login() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("citizen");
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    async function handleLogin(e) {
        e.preventDefault();
        setLoading(true);
        setErrorMsg("");

        const body = { email, password, role };

        const res = await apiPost("/auth/login", body);

        if (res.status !== 200) {
            setErrorMsg("Invalid credentials");
            setLoading(false);
            return;
        }

        const { token } = res.data;

        // Save login state
        saveAuth(email, role, token);

        navigate("/home");
    }

    return (
        <div className="auth-container">
            <div className="auth-box glass-card">
                <h1 className="logo-text">RS</h1>
                <p className="subtitle">Welcome Back</p>

                <div className="role-switch">
                    <button
                        className={role === "citizen" ? "active" : ""}
                        onClick={() => setRole("citizen")}
                    >
                        Citizen
                    </button>

                    <button
                        className={role === "authority" ? "active" : ""}
                        onClick={() => setRole("authority")}
                    >
                        Authority
                    </button>
                </div>

                <form onSubmit={handleLogin}>
                    <label>Email</label>
                    <input
                        type="email"
                        value={email}
                        placeholder="Enter email"
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <label>Password</label>
                    <input
                        type="password"
                        value={password}
                        placeholder="Enter password"
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    {errorMsg && <p className="error-text">{errorMsg}</p>}

                    <button className="auth-btn" disabled={loading}>
                        {loading ? "Logging in..." : "Login"}
                    </button>
                </form>

                <p className="switch-text">
                    New user?{" "}
                    <span onClick={() => navigate("/register")}>Create account</span>
                </p>
            </div>
        </div>
    );
}
