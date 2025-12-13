// src/App.jsx
import { Routes, Route, Navigate, useLocation } from "react-router-dom";

import NavBar from "./components/NavBar";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import MapPage from "./pages/MapPage";
import Report from "./pages/Report";
import Account from "./pages/Account";

import { isLoggedIn, getRole } from "./utils/auth";

export default function App() {
    const location = useLocation();

    // Hide navbar on login/register pages
    const hideNav =
        location.pathname === "/login" || location.pathname === "/register";

    // Protected route wrapper
    function PrivateRoute({ children }) {
        return isLoggedIn() ? children : <Navigate to="/login" replace />;
    }

    // Authority-only wrapper
    function AuthorityRoute({ children }) {
        return getRole() === "authority"
            ? children
            : <Navigate to="/home" replace />;
    }

    return (
        <div className="min-h-screen bg-black text-white">
            {!hideNav && <NavBar />}

            {/* Routes is fully compatible with future flags */}
            <Routes>
                {/* PUBLIC ROUTES */}
                <Route
                    path="/login"
                    element={
                        isLoggedIn() ? (
                            <Navigate to="/home" replace />
                        ) : (
                            <Login />
                        )
                    }
                />

                <Route
                    path="/register"
                    element={
                        isLoggedIn() ? (
                            <Navigate to="/home" replace />
                        ) : (
                            <Register />
                        )
                    }
                />

                {/* DEFAULT REDIRECT */}
                <Route path="/" element={<Navigate to="/home" replace />} />

                {/* PRIVATE ROUTES */}
                <Route
                    path="/home"
                    element={
                        <PrivateRoute>
                            <Home />
                        </PrivateRoute>
                    }
                />

                <Route
                    path="/dashboard"
                    element={
                        <PrivateRoute>
                            <Dashboard />
                        </PrivateRoute>
                    }
                />

                <Route
                    path="/map"
                    element={
                        <PrivateRoute>
                            <MapPage />
                        </PrivateRoute>
                    }
                />

                <Route
                    path="/report"
                    element={
                        <PrivateRoute>
                            <Report />
                        </PrivateRoute>
                    }
                />

                <Route
                    path="/account"
                    element={
                        <PrivateRoute>
                            <Account />
                        </PrivateRoute>
                    }
                />

                {/* FUTURE AUTHORITY ROUTE */}
                <Route
                    path="/authority-tools"
                    element={
                        <AuthorityRoute>
                            <div className="p-6">Authority Only</div>
                        </AuthorityRoute>
                    }
                />
            </Routes>
        </div>
    );
}
