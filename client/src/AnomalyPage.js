import React, { useState } from "react";
import {
  MapContainer,
  TileLayer,
  LayersControl,
  FeatureGroup,
} from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import axios from 'axios';

const { BaseLayer } = LayersControl;

const onCreated = async (e) => {
  const geometry = e.layer.toGeoJSON().geometry;

  try {
    const response = await axios.post("http://localhost:8000/get_polygon/", {
      geometry: geometry,
    });
    console.log("Gönderilen polygon GeoJSON:", geometry);

    
    const { ndvi, tahmini_rekolte } = response.data;
    alert(`NDVI: ${ndvi}, Rekolte Tahmini: ${tahmini_rekolte} kg/ha`);
  } catch (error) {
    alert("Tahmin alınamadı: " + error.message);
  }
};

function SatelliteView() {
  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer center={[39.9208, 32.8541]} zoom={17} style={{ height: "100%", width: "100%" }}>
        <LayersControl position="topright">
          <BaseLayer checked name="OpenStreetMap">
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap contributors"
            />
          </BaseLayer>

          <BaseLayer name="ESRI Uydu Görünümü">
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
            />
          </BaseLayer>
        </LayersControl>

        <FeatureGroup>
          <EditControl
            position="topright"
            draw={{
              polygon: true,
              rectangle: true,
              circle: false,
              polyline: false,
              marker: false,
              circlemarker: false,
            }}
            onCreated={onCreated}
          />
        </FeatureGroup>
      </MapContainer>
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
    <div className="card">
      <h2 style={{ textAlign: "center", marginBottom: 24 }}>Anomali Tespiti</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit">
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
                  {result.is_anomaly
                    ? (() => {
                        // background dışı en yüksek olasılıklı ve %20'yi geçen sınıfı bul
                        const entries = Object.entries(result.confidence_scores || {});
                        const nonBg = entries.slice(1).filter(([_, prob]) => prob > 0.2);
                        if (nonBg.length > 0) {
                          // En yüksek olasılıklı olanı seç
                          const [anomClass] = nonBg.reduce((a, b) => (b[1] > a[1] ? b : a));
                          return `Anomali Belirlendi: ${anomClass.toUpperCase()}`;
                        }
                        return "Anomali Belirlendi";
                      })()
                    : "Normal"}
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
                    <div className="progress-bar-bg">
                      <div className="progress-bar-fill" style={{ width: `${Math.round(prob * 100)}%` }}></div>
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
        <div style={{ display: "flex", justifyContent: "center", gap: 0, marginBottom: 32 }}>
          <button
            className={`tab-btn${tab === "satellite" ? " active" : ""}`}
            onClick={() => setTab("satellite")}
          >
            Uydu Görüntüsü
          </button>
          <button
            className={`tab-btn${tab === "anomaly" ? " active" : ""}`}
            onClick={() => setTab("anomaly")}
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