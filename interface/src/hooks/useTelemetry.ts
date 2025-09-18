import { useEffect, useState } from "react";
import type { TelemetriaData } from "../types/TelemetriaData";

export function useTelemetry() {
    // State to hold the incoming telemetry data
    const [data, setData] = useState<TelemetriaData | null>(null);

    // State to hold the user-provided server IP
    const [serverIp, setServerIp] = useState<string | null>(null);

    // Prompt the user for the server IP only once when the component mounts
    useEffect(() => {
        const ip = window.prompt("Por favor, insira o endereço IP do servidor WebSocket (Ex: localhost):");

        // Regex to validate a simple hostname or IP address.
        const validIpRegex = /^[a-zA-Z0-9\.\-_]+$/;

        if (ip && (validIpRegex.test(ip) || ip === "localhost")) {
            setServerIp(ip);
        } else if (ip) {
            // Alert the user to the invalid input if they entered something
            alert("Formato de IP do servidor inválido.");
        }
        // The empty dependency array [] ensures this effect runs only once.
    }, []);

    // Establish and manage the WebSocket connection based on the serverIp
    useEffect(() => {
        // If no server IP is set (e.g., user cancelled the prompt), do nothing.
        if (!serverIp) {
            return;
        }

        // The URL format is `ws://[IP_ADDRESS]:8000/ws/telemetry`.
        const ws = new WebSocket(`ws://${serverIp}:8000/ws/telemetry`);

        // Event handler for incoming messages from the server
        ws.onmessage = (event) => {
            try {
                // Parse the JSON data from the message
                const parsed = JSON.parse(event.data);
                setData(parsed);
            } catch (e) {
                console.error("Failed to parse WebSocket message:", e);
            }
        };

        // Event handler for WebSocket errors
        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        // Cleanup function to close the WebSocket connection when the component unmounts
        // or the serverIp changes (though it shouldn't change after the initial prompt).
        return () => {
            ws.close();
        };

    }, [serverIp]); // Rerun this effect whenever the serverIp state changes

    // Return the latest data received
    return data;
}
