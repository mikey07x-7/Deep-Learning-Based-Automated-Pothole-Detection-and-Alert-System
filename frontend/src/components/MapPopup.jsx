// src/components/MapPopup.jsx
import mapboxgl from "mapbox-gl";
import { useEffect, useRef } from "react";
import "../styles/Map.css";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_KEY;

export default function MapPopup({ item, close }) {
    const mapRef = useRef(null);

    useEffect(() => {
        if (!item) return;

        const map = new mapboxgl.Map({
            container: mapRef.current,
            style: "mapbox://styles/mapbox/dark-v11",
            center: [item.longitude, item.latitude],
            zoom: 14,
        });

        new mapboxgl.Marker({ color: "red" })
            .setLngLat([item.longitude, item.latitude])
            .addTo(map);

        return () => map.remove();
    }, [item]);

    return (
        <div className="popup-overlay">
            <div className="popup-box glass-card">
                <button className="close-btn" onClick={close}>✕</button>

                <h2 className="popup-title">Detection Location</h2>

                <div ref={mapRef} className="popup-map"></div>

                <a
                    href={`https://www.google.com/maps?q=${item.latitude},${item.longitude}`}
                    target="_blank"
                    className="btn-blue mt-4 block text-center"
                >
                    Get Directions
                </a>
            </div>
        </div>
    );
}
