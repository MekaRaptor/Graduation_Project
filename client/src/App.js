import React from "react";
import {
  MapContainer,
  TileLayer,
  LayersControl,
  FeatureGroup
} from "react-leaflet";
import { EditControl } from "react-leaflet-draw";
import axios from "axios";

import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";

const { BaseLayer } = LayersControl;

const App = () => {
  const onCreated = async (e) => {
  const geometry = e.layer.toGeoJSON().geometry;

  try {
    const response = await axios.post("http://localhost:8000/predict/", {
      geometry: geometry,
    });
    console.log("Gönderilen polygon GeoJSON:", geometry);

    
    const { ndvi, tahmini_rekolte } = response.data;
    alert(`NDVI: ${ndvi}, Rekolte Tahmini: ${tahmini_rekolte} kg/ha`);
  } catch (error) {
    alert("Tahmin alınamadı: " + error.message);
  }
};

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
};

export default App;
