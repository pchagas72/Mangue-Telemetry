// src/components/Mapa.tsx
import { MapContainer, TileLayer, Marker, Polyline, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect } from "react";

const marcadorIcon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

interface MapaProps {
    latitude: number;
    longitude: number;
    caminho: [number, number][];
}

export function Mapa({ latitude, longitude, caminho }: MapaProps) {
    if (typeof latitude !== "number" || typeof longitude !== "number") return null;
    return (
        <MapContainer
            center={[latitude, longitude]}
            zoom={17}
            scrollWheelZoom={false}
            style={{ height: "100%", width: "100%" }}
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution="Map data © OpenStreetMap contributors"
            />
            <Marker position={[latitude, longitude]} icon={marcadorIcon} />
            <Polyline positions={caminho} color="red" />
            <MapUpdater lat={latitude} lon={longitude} />
        </MapContainer>
    );
}

// Atualiza o foco do mapa dinamicamente
function MapUpdater({ lat, lon }: { lat: number; lon: number }) {
    const map = useMap();
    useEffect(() => {
        map.setView([lat, lon]);
    }, [lat, lon, map]);
    return null;
}

