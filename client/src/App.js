import React from "react";

//import { EditControl } from "react-leaflet-draw";
//import axios from "axios";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
//import HomePage from "./HomePage";
import AnomalyPage from "./AnomalyPage";
//const { BaseLayer } = LayersControl;

const App = () => {
  return (
    <Router>
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <ul>
          <li><Link to="/">Ana Sayfa</Link></li>
          <li><Link to="/anomaly">Anomali Tespiti</Link></li>
        </ul>
        <img src="/Web_logo.png" alt="Logo" style={{ height: 40, marginRight: 24 }} />
      </nav>
      <Routes>
        <Route path="/anomaly" element={<AnomalyPage />} />
      </Routes>
    </Router>
  );
};

export default App;