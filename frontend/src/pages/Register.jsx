// src/pages/Register.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiPost } from "../utils/api";
import { saveAuth } from "../utils/auth";
import "../styles/Auth.css";

export default function Register() {
    const navigate = useNavigate();

    const [role, setRole] = useState("citizen");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [name, setName] = useState("");
    const [city, setCity] = useState("");

    const [otp, setOtp] = useState("");
    const [step, setStep] = useState(1);

    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState("");

    // -----------------------
    // SEND OTP
    // -----------------------
    async function sendOtp() {
        setLoading(true);
        setMsg("");

        const res = await apiPost("/auth/send-register-otp", { email });
        setLoading(false);

        if (res.status === 200) {
            setMsg("OTP sent to email");
            setStep(2);
        } else {
            setMsg("Failed to send OTP");
        }
    }

    // -----------------------
    // VERIFY OTP
    // -----------------------
    async function verifyOtp() {
        setLoading(true);

        const res = await apiPost("/auth/verify-register-otp", {
            email,
            otp
        });

        setLoading(false);

        if (res.status === 200) {
            setStep(3);
        } else {
            setMsg("Invalid OTP");
        }
    }

    // -----------------------
    // FINAL REGISTER
    // -----------------------
    async function submitRegister() {
        setLoading(true);

        const res = await apiPost("/auth/register", {
            email,
            password,
            role,
            name,
            city
        });

        setLoading(false);

        if (res.status === 200) {
            saveAuth(email, role, res.data.token);
            navigate("/home");
        } else {
            setMsg("Registration failed");
        }
    }

    return (
        <div className="auth-container">
            <div className="auth-box glass-card">
                <h1 className="logo-text">RS</h1>
                <p className="subtitle">Create Account</p>

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

                {/* STEP 1 — EMAIL */}
                {step === 1 && (
                    <div>
                        <label>Email</label>
                        <input
                            type="email"
                            placeholder="Enter email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />

                        <button className="auth-btn" onClick={sendOtp}>
                            {loading ? "Sending..." : "Send OTP"}
                        </button>
                    </div>
                )}

                {/* STEP 2 — OTP */}
                {step === 2 && (
                    <div>
                        <label>Enter OTP</label>
                        <input
                            type="text"
                            placeholder="6-digit OTP"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                        />

                        <button className="auth-btn" onClick={verifyOtp}>
                            {loading ? "Checking..." : "Verify OTP"}
                        </button>
                    </div>
                )}

                {/* STEP 3 — NAME + CITY + PASSWORD */}
                {step === 3 && (
                    <div>
                        <label>Full Name</label>
                        <input
                            type="text"
                            placeholder="Your name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />

                        <label>City</label>
                        <input
                            type="text"
                            placeholder="City name"
                            value={city}
                            onChange={(e) => setCity(e.target.value)}
                        />

                        <label>Create Password</label>
                        <input
                            type="password"
                            placeholder="Choose a password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />

                        <button className="auth-btn" onClick={submitRegister}>
                            {loading ? "Creating..." : "Register"}
                        </button>
                    </div>
                )}

                {msg && <p className="info-text">{msg}</p>}

                <p className="switch-text">
                    Already have an account?{" "}
                    <span onClick={() => navigate("/login")}>Login</span>
                </p>
            </div>
        </div>
    );
}
