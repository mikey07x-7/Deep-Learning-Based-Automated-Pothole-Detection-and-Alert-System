// src/pages/Dashboard.jsx

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../utils/api";
import DetectionCard from "../components/DetectionCard";
import MapPopup from "../components/MapPopup";
import { getRole } from "../utils/auth";
import "../styles/Dashboard.css";

export default function Dashboard() {
    const [list, setList] = useState([]);
    const [popupItem, setPopupItem] = useState(null);
    const role = getRole();

    async function loadDetections() {
        const res = await apiGet("/api/detections?order=desc");

        if (res.status === 200) {
            console.log("Backend response:", res.data);

            // IMPORTANT FIX → ensure array
            setList(res.data.detections || []);
        }
    }

    async function markAsFixed(id) {
        const res = await apiPost("/api/detections/fix", { id });
        if (res.status === 200) loadDetections();
        else alert("Failed marking fixed");
    }

    useEffect(() => {
        loadDetections();
        const interval = setInterval(loadDetections, 4000);
        return () => clearInterval(interval);
    }, []);

    const total = list.length;
    const fixedCount = list.filter((d) => d.status === "fixed").length;
    const notFixedCount = total - fixedCount;

    return (
        <div className="dashboard-container">
            <div className="stats-row">
                <div className="stat-box glass-card">
                    <h3>Total</h3>
                    <p>{total}</p>
                </div>
                <div className="stat-box glass-card">
                    <h3>Fixed</h3>
                    <p className="text-green-400">{fixedCount}</p>
                </div>
                <div className="stat-box glass-card">
                    <h3>Not Fixed</h3>
                    <p className="text-red-400">{notFixedCount}</p>
                </div>
            </div>

            <h2 className="section-title">All Detections</h2>

            <div className="detect-grid">
                {list.map((item) => (
                    <DetectionCard
                        key={item.id}
                        item={item}
                        openPopup={setPopupItem}
                        canFix={role === "authority"}
                        onFix={() => markAsFixed(item.id)}
                    />
                ))}
            </div>

            {popupItem && (
                <MapPopup item={popupItem} close={() => setPopupItem(null)} />
            )}
        </div>
    );
}
