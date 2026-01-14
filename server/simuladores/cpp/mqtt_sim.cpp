#include <iostream>
#include <cmath>
#include <chrono>
#include <thread>
#include <mosquittopp.h>

using namespace std;
using namespace std::chrono;

// Settings from server/settings.py
#define MQTT_HOST "44dbd06832c54083bd5d0cacdb217aff.s1.eu.hivemq.cloud"
#define MQTT_PORT 8883
#define MQTT_TOPIC "/logging"
#define MQTT_CLIENT_ID "Mangu3Baja_Sim_CPP"
#define MQTT_USERNAME ""
#define MQTT_PASSWORD ""

// Path to system CA certificates (Standard on Ubuntu/Debian/Arch)
// If this file does not exist, try "/etc/pki/tls/certs/ca-bundle.crt" (Fedora/RHEL)
#define CA_CERT_PATH "/etc/ssl/certs/ca-certificates.crt"


#pragma pack(push, 1)

typedef struct {
    int16_t acc_x;
    int16_t acc_y;
    int16_t acc_z;
} imu_acc_t;

typedef struct {
    int16_t dps_x;
    int16_t dps_y;
    int16_t dps_z;
} imu_dps_t;

typedef struct {
    int16_t Roll;
    int16_t Pitch;
} Angle_t;

typedef struct {
    float volt;
    uint8_t SOC;
    uint8_t cvt;
    float current;
    uint8_t temperature;
    uint16_t speed;
    imu_acc_t imu_acc;
    imu_dps_t imu_dps;
    Angle_t Angle;
    uint16_t rpm;
    uint8_t flags;
    double latitude;
    double longitude;
    uint32_t timestamp;
} mqtt_packet_t;

#pragma pack(pop)

class MQTTClient : public mosqpp::mosquittopp {
public:
    MQTTClient(const char* id, const char* host, int port)
        : mosquittopp(id), counter(0) {
        
        // Setup credentials
        username_pw_set(MQTT_USERNAME, MQTT_PASSWORD);

        // Required for HiveMQ Cloud (TLS)
        // We MUST provide a CA file. passing NULL causes "Invalid arguments"
        int tls_rc = tls_set(CA_CERT_PATH, NULL, NULL, NULL, NULL);
        
        if(tls_rc != MOSQ_ERR_SUCCESS){
            cerr << "[FATAL] Failed to setup TLS: " << mosquitto_strerror(tls_rc) << endl;
            cerr << "        Make sure " << CA_CERT_PATH << " exists on your system." << endl;
            exit(1); // Stop execution if TLS fails
        }

        // Connect asynchronously
        int rc = connect_async(host, port, 60);
        if (rc != MOSQ_ERR_SUCCESS) {
             cerr << "[ERROR] Connection failed: " << mosquitto_strerror(rc) << endl;
        }
    }

    void on_connect(int rc) override {
        if (rc == 0) {
            cout << "[MQTT] Connected successfully to Broker!" << endl;
        } else {
            cout << "[MQTT] Connection Failed! Error Code: " << rc << endl;
        }
    }

    void on_disconnect(int rc) override {
        cout << "[MQTT] Disconnected! Code: " << rc << endl;
    }

    void on_log(int level, const char *str) override {
        if (level == MOSQ_LOG_ERR || level == MOSQ_LOG_WARNING) {
            cout << "[LIB_LOG] " << str << endl;
        }
    }

    void loop_simulacao() {
        while (true) {
            mqtt_packet_t pkt = gerar_pacote();
            
            int counter = 0;
                if (counter == 10){
                    int rc = publish(nullptr, MQTT_TOPIC, sizeof(pkt), &pkt, 1, false);

                    if(rc != MOSQ_ERR_SUCCESS){
                        cerr << "[ERROR] Publish failed: " << mosquitto_strerror(rc) << endl;
                        reconnect();
                        this_thread::sleep_for(chrono::seconds(1));
                    } else {
                        cout << "[MQTT] Sending Packet " << counter << " | Speed: " << pkt.speed << " km/h" << endl;
                    }

                    counter++;
                    this_thread::sleep_for(chrono::milliseconds(500));
                }
        }
    }

private:
    uint32_t counter;

    mqtt_packet_t gerar_pacote() {
        mqtt_packet_t pkt{};
        
        pkt.volt = 12.5f + sin(counter * 0.1) * 0.5f;
        pkt.SOC = 98 - (counter % 20);
        pkt.cvt = 80 + (int)(sin(counter * 0.2) * 5);
        pkt.current = 15.3f + cos(counter * 0.1) * 2.0f;
        pkt.temperature = 75 + (int)(cos(counter * 0.3) * 3);
        pkt.speed = (counter * 2) % 60;
        
        pkt.imu_acc = {
            (int16_t)(sin(counter * 0.5) * 100),
            (int16_t)(cos(counter * 0.5) * 100),
            (int16_t)(980 + sin(counter * 0.2) * 10)
        };
        
        pkt.imu_dps = {
            (int16_t)(cos(counter * 0.4) * 50),
            (int16_t)(sin(counter * 0.4) * 50),
            (int16_t)(cos(counter * 0.1) * 5)
        };
        
        pkt.Angle = {(int16_t)(sin(counter * 0.1) * 20), (int16_t)(cos(counter * 0.1) * 10)};
        pkt.rpm = 3000 + (uint16_t)(sin(counter * 0.8) * 500);
        pkt.flags = counter % 2;
        
        pkt.latitude = -8.05428 + sin(counter * 0.01) * 0.001;
        pkt.longitude = -34.8813 + cos(counter * 0.01) * 0.001;
        
        auto now = std::chrono::system_clock::now();
        pkt.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();

        return pkt;
    }
};

int main() {
    mosqpp::lib_init();
    
    MQTTClient client(MQTT_CLIENT_ID, MQTT_HOST, MQTT_PORT);
    
    int rc = client.loop_start();
    if(rc != MOSQ_ERR_SUCCESS){
        cerr << "Failed to start network loop: " << mosquitto_strerror(rc) << endl;
        return 1;
    }

    client.loop_simulacao();
    
    mosqpp::lib_cleanup();
    return 0;
}
