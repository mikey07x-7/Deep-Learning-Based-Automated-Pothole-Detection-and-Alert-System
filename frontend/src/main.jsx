// src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./main.css";

// Remove React Router warnings by enabling future flags
const routerFutureFlags = {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
};

ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
        <BrowserRouter future={routerFutureFlags}>
            <App />
        </BrowserRouter>
    </React.StrictMode>
);
