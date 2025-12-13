// src/components/DetectionCard.jsx

export default function DetectionCard({ item, openPopup, canFix, onFix }) {
    // Correct Supabase image URL
    const imgUrl = item.image_url || "/placeholder.jpg";

    return (
        <div className="detect-card glass-card">
            
            {/* IMAGE FIXED */}
            <img
                src={imgUrl}
                className="detect-image"
                alt="pothole"
                onError={(e) => (e.target.src = "/placeholder.jpg")}
            />

            <div className="detect-body">
                <p><strong>Location:</strong> {item.latitude}, {item.longitude}</p>
                <p><strong>Confidence:</strong> {Math.round(item.confidence * 100)}%</p>

                {/* STATUS BADGE */}
                <span
                    className={`status-badge ${
                        item.status === "fixed" ? "fixed" : "not-fixed"
                    }`}
                >
                    {item.status === "fixed" ? "Fixed" : "Not Fixed"}
                </span>

                {/* ACTION BUTTONS */}
                <div className="detect-actions">
                    <button className="btn-blue-small" onClick={() => openPopup(item)}>
                        View on Map
                    </button>

                    <a
                        className="btn-outline-small"
                        href={`https://www.google.com/maps?q=${item.latitude},${item.longitude}`}
                        target="_blank"
                    >
                        Directions
                    </a>
                </div>

                {/* AUTHORITY-ONLY ACTION */}
                {canFix && item.status !== "fixed" && (
                    <button className="btn-green" onClick={onFix}>
                        Mark as Fixed
                    </button>
                )}
            </div>
        </div>
    );
}
