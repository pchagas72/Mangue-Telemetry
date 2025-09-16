// receiver_emulator.cpp
//
// This program emulates the ESP32 LoRa receiver device to test the Python server.
// It sends a start marker followed by a binary packet over a specified serial port.
//
// How to compile:
//   Linux/macOS: g++ -o receiver_emulator receiver_emulator.cpp -std=c++11
//   Windows (MinGW): g++ -o receiver_emulator.exe receiver_emulator.cpp -std=c++11
//
// How to run:
//   Linux/macOS: ./receiver_emulator /dev/ttyUSB0
//   Windows:     receiver_emulator.exe COM3
//
// Note: You might need to create a virtual serial port pair for testing.
//   - Linux: socat -d -d pty,raw,echo=0 pty,raw,echo=0
//   - Windows: com0com (third-party utility)

#include <iostream>
#include <cstdint>
#include <chrono>
#include <thread>
#include <cmath>
#include <string>
#include <vector>

// Platform-specific headers for serial communication
#ifdef _WIN32
#include <windows.h>
#else
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#endif

// --- Packet Definition (Copied EXACTLY from your packets.h) ---
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
} radio_packet_t;

#pragma pack(pop)
// --- End of Packet Definition ---


// --- Serial Port Handler ---
class SerialPort {
private:
#ifdef _WIN32
    HANDLE hSerial;
#else
    int serial_port;
#endif

public:
    SerialPort() {
#ifdef _WIN32
        hSerial = INVALID_HANDLE_VALUE;
#else
        serial_port = -1;
#endif
    }

    bool open(const std::string& port_name, int baudrate) {
#ifdef _WIN32
        hSerial = CreateFile(port_name.c_str(), GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
        if (hSerial == INVALID_HANDLE_VALUE) {
            return false;
        }
        DCB dcbSerialParams = {0};
        dcbSerialParams.DCBlength = sizeof(dcbSerialParams);
        if (!GetCommState(hSerial, &dcbSerialParams)) {
            close();
            return false;
        }
        dcbSerialParams.BaudRate = baudrate;
        dcbSerialParams.ByteSize = 8;
        dcbSerialParams.StopBits = ONESTOPBIT;
        dcbSerialParams.Parity = NOPARITY;
        if (!SetCommState(hSerial, &dcbSerialParams)) {
            close();
            return false;
        }
        return true;
#else
        serial_port = ::open(port_name.c_str(), O_RDWR);
        if (serial_port < 0) {
            return false;
        }
        struct termios tty;
        if (tcgetattr(serial_port, &tty) != 0) {
            close();
            return false;
        }
        cfsetispeed(&tty, baudrate);
        cfsetospeed(&tty, baudrate);
        tty.c_cflag &= ~PARENB;
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CSIZE;
        tty.c_cflag |= CS8;
        tty.c_cflag &= ~CRTSCTS;
        tty.c_cflag |= CREAD | CLOCAL;
        tty.c_lflag &= ~ICANON;
        tty.c_lflag &= ~ECHO;
        tty.c_lflag &= ~ECHOE;
        tty.c_lflag &= ~ECHONL;
        tty.c_lflag &= ~ISIG;
        tty.c_iflag &= ~(IXON | IXOFF | IXANY);
        tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
        tty.c_oflag &= ~OPOST;
        tty.c_oflag &= ~ONLCR;
        tty.c_cc[VTIME] = 0;
        tty.c_cc[VMIN] = 0;
        if (tcsetattr(serial_port, TCSANOW, &tty) != 0) {
            close();
            return false;
        }
        return true;
#endif
    }

    int write_data(const uint8_t* buffer, size_t size) {
#ifdef _WIN32
        DWORD bytes_written;
        if (!WriteFile(hSerial, buffer, size, &bytes_written, NULL)) {
            return -1;
        }
        return bytes_written;
#else
        return ::write(serial_port, buffer, size);
#endif
    }

    void close() {
#ifdef _WIN32
        if (hSerial != INVALID_HANDLE_VALUE) {
            CloseHandle(hSerial);
            hSerial = INVALID_HANDLE_VALUE;
        }
#else
        if (serial_port >= 0) {
            ::close(serial_port);
            serial_port = -1;
        }
#endif
    }

    ~SerialPort() {
        close();
    }
};

// --- Data Simulation ---
void populate_packet(radio_packet_t& pkt, uint32_t counter) {
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
}


// --- Main Application ---
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Error: Please provide the serial port name as an argument." << std::endl;
        std::cerr << "Usage (Linux/macOS): " << argv[0] << " /dev/ttyUSB0" << std::endl;
        std::cerr << "Usage (Windows):   " << argv[0] << " COM3" << std::endl;
        return 1;
    }

    std::string port_name = argv[1];
    int baud_rate = 115200;

    SerialPort serial;
    if (!serial.open(port_name, B115200)) { // Note: B115200 is for termios, Windows uses the int directly
        std::cerr << "Error: Could not open serial port " << port_name << std::endl;
        return 1;
    }

    std::cout << "Successfully opened serial port " << port_name << " at " << baud_rate << " baud." << std::endl;
    std::cout << "Starting data emulation. Press Ctrl+C to exit." << std::endl;

    const uint8_t start_marker[] = {0xAA, 0xBB, 0xCC, 0xDD};
    radio_packet_t packet_to_send;
    uint32_t counter = 0;

    while (true) {
        // 1. Populate the struct with new simulated data
        populate_packet(packet_to_send, counter);

        // 2. Send the start marker
        serial.write_data(start_marker, sizeof(start_marker));

        // 3. Send the raw binary data of the struct
        serial.write_data(reinterpret_cast<const uint8_t*>(&packet_to_send), sizeof(packet_to_send));
        
        std::cout << "Sent packet " << counter << " (Speed: " << packet_to_send.speed << " km/h)" << std::endl;

        counter++;
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    serial.close();
    return 0;
}
