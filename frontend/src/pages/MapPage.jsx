// src/pages/MapPage.jsx

import mapboxgl from "mapbox-gl";
import { useEffect, useRef, useState } from "react";
import { apiGet } from "../utils/api";
import "../styles/Map.css";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_KEY;

export default function MapPage() {
    const mapRef = useRef(null);
    const mapInstance = useRef(null);
    const [detections, setDetections] = useState([]);

    async function loadDetections() {
        const res = await apiGet("/api/detections?order=desc");

        if (res.status === 200) {
            console.log("Map detections:", res.data);

            // FIX: Extract from { detections: [...] }
            setDetections(res.data.detections || []);
        }
    }

    useEffect(() => {
        loadDetections();
    }, []);

    useEffect(() => {
        if (!mapRef.current) return;

        mapInstance.current = new mapboxgl.Map({
            container: mapRef.current,
            style: "mapbox://styles/mapbox/dark-v11",
            center: [77.59, 12.97],
            zoom: 11,
        });

        return () => mapInstance.current.remove();
    }, []);

    useEffect(() => {
        if (!mapInstance.current) return;

        // Clear existing markers (optional future improvement)

        // Add new markers
        (detections || []).forEach((d) => {
            const markerColor = d.status === "fixed" ? "#22c55e" : "#ef4444";

            const popupHTML = `
                <div style="color:white;">
                    <h3>Pothole Detection</h3>
                    <p><b>Date:</b> ${d.date}</p>
                    <p><b>Time:</b> ${d.time}</p>
                    <p><b>Confidence:</b> ${d.confidence}</p>
                    <p><b>Status:</b> ${d.status}</p>
                    <a href="https://www.google.com/maps?q=${d.latitude},${d.longitude}" 
                       target="_blank"
                       style="color:#60a5fa; text-decoration:underline;">
                       Get Directions
                    </a>
                </div>
            `;

            new mapboxgl.Marker({ color: markerColor })
                .setLngLat([d.longitude, d.latitude])
                .setPopup(new mapboxgl.Popup().setHTML(popupHTML))
                .addTo(mapInstance.current);
        });
    }, [detections]);

    return (
        <div className="mappage-container">
            <div className="map-title-box glass-card">
                <h1 className="map-title">Detection Map</h1>
                <p className="map-subtitle">{detections.length} potholes detected</p>
            </div>

            <div ref={mapRef} className="map-canvas"></div>
        </div>
    );
}
