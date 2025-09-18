#include <iostream>
#include <random>
#include <chrono>
#include <thread>
#include <mosquittopp.h>

using namespace std;
using namespace std::chrono;

const std::string SERVER_ADDRESS("tcp://YOUR_SERVER_IP_HERE:1883");

#pragma pack(push, 1) // garante alinhamento idêntico ao do firmware

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
        : mosquittopp(id), start_time(steady_clock::now()), last_vel(0.0) {
        connect(host, port, 60);
    }

    void on_connect(int rc) override {
        if (rc == 0)
            cout << "[MQTT] Conectado com sucesso!" << endl;
        else
            cout << "[MQTT] Falha na conexão: " << rc << endl;
    }

    void loop_simulacao() {
        while (true) {
            mqtt_packet_t pkt = gerar_pacote();
            publish(nullptr, "/logging", sizeof(pkt), &pkt, 1, false);
            cout << "[MQTT] Pacote binário enviado (" << sizeof(pkt) << " bytes)" << endl;
            this_thread::sleep_for(chrono::milliseconds(50));
        }
    }

private:
    steady_clock::time_point start_time;
    double last_vel;

    mqtt_packet_t gerar_pacote() {
        double t = duration<double>(steady_clock::now() - start_time).count();
        mqtt_packet_t pkt{};

        double vel = max(0.0, min(60.0, 30.0 + 15.0 * sin(t / 10.0)));
        double rpm = vel * 120 + randomf(-200, 200);
        double accx = (vel - last_vel) / 0.5;

        pkt.volt = 13.0f - t * 0.001f;
        pkt.SOC = static_cast<uint8_t>(max(0.0, 100.0 - t * 0.03));
        pkt.cvt = static_cast<uint8_t>(min(95.0, 50.0 + t * 0.25));
        pkt.current = static_cast<float>(randomf(150, 300));
        pkt.temperature = static_cast<uint8_t>(min(110.0, 60.0 + t * 0.3));
        pkt.speed = static_cast<uint16_t>(vel * 3.6);

        pkt.imu_acc = { static_cast<int16_t>(accx * 100),
                        static_cast<int16_t>(randomf(-20, 20)),
                        static_cast<int16_t>(randomf(940, 980)) };

        pkt.imu_dps = { static_cast<int16_t>(randomf(-100, 100)),
                        static_cast<int16_t>(randomf(-100, 100)),
                        static_cast<int16_t>(randomf(-100, 100)) };

        pkt.Angle = { static_cast<int16_t>(randomf(-500, 500)),
                      static_cast<int16_t>(randomf(-500, 500)) };

        pkt.rpm = static_cast<uint16_t>(rpm);
        pkt.flags = 0b00000001;

        pkt.latitude = -8.05428 + t * 0.00002;
        pkt.longitude = -34.8813 + sin(t / 20.0) * 0.0001;
        pkt.timestamp = static_cast<uint32_t>(t * 1000);

        last_vel = vel;
        return pkt;
    }

    double randomf(double min, double max) {
        static random_device rd;
        static mt19937 gen(rd());
        uniform_real_distribution<> dis(min, max);
        return dis(gen);
    }
};

int main() {
    mosqpp::lib_init();
    MQTTClient client("simulador_bin", "YOUR_SERVER_IP_HERE", 1883);  // <- Aqui foi alterado
    client.username_pw_set("", "");
    client.loop_start();
    client.loop_simulacao();
    mosqpp::lib_cleanup();
    return 0;
}

