// src/pages/Home.jsx
import { useEffect, useState } from "react";
import { apiGet } from "../utils/api";
import DetectionCard from "../components/DetectionCard";
import MapPopup from "../components/MapPopup";
import "../styles/Home.css";

export default function Home() {
    const [recent, setRecent] = useState([]);
    const [popupItem, setPopupItem] = useState(null);

    async function loadRecent() {
        const res = await apiGet("/api/recent-detections");

        if (res.status === 200) {
            console.log("Recent detections:", res.data);

            // FIX: Extract from { detections: [...] }
            setRecent(res.data.detections || []);
        }
    }

    useEffect(() => {
        loadRecent();
    }, []);

    return (
        <div className="home-container">
            {/* HERO HEADER */}
            <div className="home-hero">
                <h1 className="home-title">RoadSense Dashboard</h1>
                <p className="home-subtitle">
                    Real-time pothole reporting & AI detection system
                </p>

                <div className="home-buttons">
                    <a href="/report" className="btn-blue">Report Pothole</a>
                    <a href="/map" className="btn-dark">View Map</a>
                    <a href="/dashboard" className="btn-outline">Dashboard</a>
                </div>
            </div>

            {/* RECENT DETECTIONS */}
            <h2 className="section-title">Recent Detections</h2>

            <div className="detect-grid">
                {recent.length === 0 && (
                    <p className="text-gray-400 text-center w-full">
                        No detections yet.
                    </p>
                )}

                {recent.map((item) => (
                    <DetectionCard
                        key={item.id}
                        item={item}
                        openPopup={setPopupItem}
                    />
                ))}
            </div>

            {popupItem && (
                <MapPopup item={popupItem} close={() => setPopupItem(null)} />
            )}
        </div>
    );
}
