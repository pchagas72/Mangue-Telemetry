// src/components/Mapa.tsx
import { MapContainer, TileLayer, Marker, Polyline, useMap, Circle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect } from "react";

const marcadorIcon = L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

// Added optional sfLocation argument
export function Mapa(
    latitude: number, 
    longitude: number, 
    caminho: [number, number][], 
    sfLocation?: { lat: number, lon: number } | null
) {
    if (typeof latitude !== "number" || typeof longitude !== "number") return null;

    // Safety check for path array
    const safeCaminho = Array.isArray(caminho) ? caminho : [];

    return (
        <MapContainer
            center={[latitude, longitude]}
            zoom={18} 
            scrollWheelZoom={true} 
            style={{ height: "100%", width: "100%" }}
        >
            <TileLayer
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                attribution="Tiles &copy; Esri &mdash; Source: Esri..."
            />

            <Marker position={[latitude, longitude]} icon={marcadorIcon} />
            
            <Polyline positions={safeCaminho} color="yellow" weight={4} />
            
            {/* Render S/F Line if it exists */}
            {sfLocation && (
                <Circle 
                    center={[sfLocation.lat, sfLocation.lon]}
                    pathOptions={{ color: 'white', fillColor: 'white', fillOpacity: 0.5 }}
                    radius={3} // 3 meters radius
                />
            )}
            
            <MapUpdater lat={latitude} lon={longitude} />
        </MapContainer>
    );
}

function MapUpdater({ lat, lon }: { lat: number; lon: number }) {
    const map = useMap();
    useEffect(() => {
        map.setView([lat, lon]);
    }, [lat, lon, map]);
    return null;
}
