import React, { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, LayersControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";

function SatelliteView() {
  return (
    <div style={{ textAlign: "center", marginTop: 40 }}>
      <h3>Uydu Görüntüsü</h3>
      <div style={{ color: '#888', marginTop: 24 }}>
        Burada uydu haritası veya görseli gösterilecek (placeholder).
      </div>
      <div style={{ margin: "32px auto", maxWidth: 900, height: 400 }}>
        <MapContainer center={[39.9208, 32.8541]} zoom={15} style={{ height: "100%", width: "100%", borderRadius: 12, boxShadow: "0 2px 12px #0001" }}>
          <LayersControl position="topright">
            <LayersControl.BaseLayer checked name="OpenStreetMap">
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution="&copy; OpenStreetMap contributors"
              />
            </LayersControl.BaseLayer>
            <LayersControl.BaseLayer name="ESRI Uydu Görünümü">
              <TileLayer
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
              />
            </LayersControl.BaseLayer>
          </LayersControl>
        </MapContainer>
      </div>
    </div>
  );
}

function AnomalyDetection() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await axios.post(
        "http://localhost:8000/detect-anomaly/",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(response.data);
    } catch (error) {
      setResult({ error: "Bir hata oluştu" });
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 500, margin: "40px auto", padding: 24, background: "#fff", borderRadius: 12, boxShadow: "0 2px 12px #0001" }}>
      <h2 style={{ textAlign: "center", marginBottom: 24 }}>Anomali Tespiti</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <input type="file" accept="image/*" onChange={handleFileChange} style={{ padding: 8, borderRadius: 6, border: "1px solid #ccc" }} />
        <button type="submit" style={{ padding: 10, borderRadius: 6, background: "#1976d2", color: "#fff", border: "none", fontWeight: 600, cursor: "pointer" }}>
          {loading ? "Yükleniyor..." : "Gönder"}
        </button>
      </form>
      {result && (
        <div style={{ marginTop: 32 }}>
          {result.error ? (
            <div style={{ color: "#d32f2f", fontWeight: 600 }}>{result.error}</div>
          ) : (
            <>
              <h3 style={{ textAlign: "center", marginBottom: 16 }}>Sonuçlar</h3>
              <div style={{ marginBottom: 16, textAlign: "center" }}>
                <span style={{ fontWeight: 600, fontSize: 18 }}>
                  {result.primary_class?.name?.toUpperCase() || "-"}
                </span>
                <br />
                <span style={{ color: result.is_anomaly ? "#d32f2f" : "#388e3c", fontWeight: 600 }}>
                  {result.is_anomaly ? "Anomali Tespit Edildi" : "Normal"}
                </span>
                <br />
                <span style={{ fontSize: 14, color: "#888" }}>
                  Güven: %{Math.round((result.primary_class?.probability || 0) * 100)}
                </span>
              </div>
              <div>
                {result.confidence_scores && Object.entries(result.confidence_scores).map(([className, prob]) => (
                  <div key={className} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
                      <span>{className}</span>
                      <span>%{Math.round(prob * 100)}</span>
                    </div>
                    <div style={{ background: "#eee", borderRadius: 6, height: 10, overflow: "hidden" }}>
                      <div style={{ width: `${Math.round(prob * 100)}%`, height: "100%", background: "#1976d2" }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function AnomalyPage() {
  const [tab, setTab] = useState("anomaly");

  return (
    <div style={{ minHeight: "80vh", background: "#f7f7f7" }}>
      <div style={{ maxWidth: 900, margin: "0 auto", paddingTop: 40 }}>
        <div style={{ display: "flex", justifyContent: "center", gap: 16, marginBottom: 32 }}>
          <button
            onClick={() => setTab("satellite")}
            style={{
              padding: "10px 24px",
              borderRadius: 6,
              border: tab === "satellite" ? "2px solid #1976d2" : "1px solid #ccc",
              background: tab === "satellite" ? "#e3f2fd" : "#fff",
              color: tab === "satellite" ? "#1976d2" : "#333",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            Uydu Görüntüsü
          </button>
          <button
            onClick={() => setTab("anomaly")}
            style={{
              padding: "10px 24px",
              borderRadius: 6,
              border: tab === "anomaly" ? "2px solid #1976d2" : "1px solid #ccc",
              background: tab === "anomaly" ? "#e3f2fd" : "#fff",
              color: tab === "anomaly" ? "#1976d2" : "#333",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            Anomali Tespiti
          </button>
        </div>
        {tab === "satellite" && <SatelliteView />}
        {tab === "anomaly" && <AnomalyDetection />}
      </div>
    </div>
  );
}

export default AnomalyPage; 