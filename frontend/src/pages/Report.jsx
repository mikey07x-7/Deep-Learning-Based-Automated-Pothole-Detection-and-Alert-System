// src/pages/Report.jsx
import { useState } from "react";
import { apiUpload } from "../utils/api";
import "../styles/Report.css";

export default function Report() {
    const [latitude, setLatitude] = useState("");
    const [longitude, setLongitude] = useState("");
    const [description, setDescription] = useState("");
    const [confidence, setConfidence] = useState(75);
    const [imageFile, setImageFile] = useState(null);
    const [preview, setPreview] = useState(null);

    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState("");

    // Get device GPS location
    function getCurrentLocation() {
        if (!navigator.geolocation) {
            setMsg("Geolocation not supported");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setLatitude(pos.coords.latitude.toFixed(6));
                setLongitude(pos.coords.longitude.toFixed(6));
            },
            () => setMsg("Unable to fetch location")
        );
    }

    // When a file is selected
    function handleFileChange(e) {
        const file = e.target.files[0];
        if (!file) return;

        setImageFile(file);
        setPreview(URL.createObjectURL(file));
    }

    // Submit report
    async function submitReport() {
        if (!imageFile) {
            setMsg("Please upload an image");
            return;
        }
        if (!latitude || !longitude) {
            setMsg("Please enter location coordinates");
            return;
        }

        setLoading(true);

        const form = new FormData();
        form.append("latitude", latitude);
        form.append("longitude", longitude);
        form.append("confidence", confidence);
        form.append("description", description);
        form.append("file", imageFile);

        const res = await apiUpload("/api/manual-detect", form);

        setLoading(false);

        if (res.status === 200) {
            setMsg("Report submitted successfully!");
            setImageFile(null);
            setPreview(null);
            setDescription("");
        } else {
            setMsg("Failed to submit report");
        }
    }

    return (
        <div className="report-container">
            <h1 className="report-title">Report a Pothole</h1>

            <div className="report-card glass-card">
                {/* IMAGE UPLOAD */}
                <label className="label">Upload Image</label>
                <input type="file" accept="image/*" onChange={handleFileChange} />

                {preview && (
                    <img
                        src={preview}
                        alt="preview"
                        className="image-preview"
                    />
                )}

                {/* LOCATION */}
                <div className="loc-row">
                    <div className="loc-item">
                        <label className="label">Latitude</label>
                        <input
                            type="text"
                            value={latitude}
                            onChange={(e) => setLatitude(e.target.value)}
                        />
                    </div>

                    <div className="loc-item">
                        <label className="label">Longitude</label>
                        <input
                            type="text"
                            value={longitude}
                            onChange={(e) => setLongitude(e.target.value)}
                        />
                    </div>
                </div>

                <button
                    className="btn-blue mt-2"
                    onClick={getCurrentLocation}
                >
                    Use My Current Location
                </button>

                {/* CONFIDENCE SLIDER */}
                <label className="label mt-4">Confidence: {confidence}%</label>
                <input
                    type="range"
                    min="1"
                    max="100"
                    value={confidence}
                    onChange={(e) => setConfidence(e.target.value)}
                />

                {/* DESCRIPTION */}
                <label className="label mt-4">Description</label>
                <textarea
                    className="desc-box"
                    placeholder="Enter description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />

                {/* SUBMIT */}
                <button
                    className="btn-blue w-full mt-4"
                    onClick={submitReport}
                    disabled={loading}
                >
                    {loading ? "Submitting..." : "Submit Report"}
                </button>

                {msg && <p className="info-text mt-3">{msg}</p>}
            </div>
        </div>
    );
}
