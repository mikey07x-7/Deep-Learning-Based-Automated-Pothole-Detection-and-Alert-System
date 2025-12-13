// src/components/NavBar.jsx
import { NavLink, useNavigate } from "react-router-dom";
import { clearAuth, getRole } from "../utils/auth";

export default function NavBar() {
    const navigate = useNavigate();
    const role = getRole();

    function logout() {
        clearAuth();
        navigate("/login");
    }

    const activeClass =
        "text-blue-400 font-semibold border-b-2 border-blue-500 pb-1";
    const baseClass =
        "text-gray-300 hover:text-white transition-all duration-150 pb-1";

    return (
        <nav className="w-full bg-[#0b0f19] shadow-lg px-6 py-3 flex items-center justify-between border-b border-white/10">
            {/* LEFT — LOGO */}
            <div
                className="text-2xl font-bold text-white cursor-pointer"
                onClick={() => navigate("/home")}
            >
                RS
            </div>

            {/* CENTER — NAV LINKS */}
            <div className="hidden md:flex gap-8 text-lg">
                <NavLink
                    to="/home"
                    className={({ isActive }) =>
                        isActive ? activeClass : baseClass
                    }
                >
                    Home
                </NavLink>

                <NavLink
                    to="/dashboard"
                    className={({ isActive }) =>
                        isActive ? activeClass : baseClass
                    }
                >
                    Dashboard
                </NavLink>

                <NavLink
                    to="/map"
                    className={({ isActive }) =>
                        isActive ? activeClass : baseClass
                    }
                >
                    Map
                </NavLink>

                <NavLink
                    to="/report"
                    className={({ isActive }) =>
                        isActive ? activeClass : baseClass
                    }
                >
                    Report
                </NavLink>

                <NavLink
                    to="/account"
                    className={({ isActive }) =>
                        isActive ? activeClass : baseClass
                    }
                >
                    Account
                </NavLink>

                {/* AUTHORITY EXTRA ITEM */}
                {role === "authority" && (
                    <NavLink
                        to="/authority-tools"
                        className={({ isActive }) =>
                            isActive ? activeClass : baseClass
                        }
                    >
                        Fix Panel
                    </NavLink>
                )}
            </div>

            {/* RIGHT — LOGOUT BUTTON */}
            <button
                onClick={logout}
                className="text-white bg-blue-600 px-4 py-2 rounded-md hover:bg-blue-700 transition-all duration-150"
            >
                Logout
            </button>
        </nav>
    );
}
