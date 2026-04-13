#include "backend.h"
#include <QDebug>
#include <cstdio>

Backend::Backend(QObject *parent) 
    : QObject(parent), m_connectionStatus("Disconnected"),
      m_speed(0), m_rpm(0), m_voltage(0), m_current(0), m_soc(0),
      m_tempMotor(0), m_tempCVT(0),
      m_accX(0), m_accY(0), m_accZ(0), m_dpsX(0), m_dpsY(0), m_dpsZ(0), m_roll(0), m_pitch(0),
      m_latitude(0), m_longitude(0), m_distance(0), m_lapDistance(0),
      m_lapCount(0), m_currentLapTime(0), m_bestLapTime(0), m_lastLapTime(0)
{
    connect(&m_webSocket, &QWebSocket::connected, this, &Backend::onConnected);
    connect(&m_webSocket, &QWebSocket::disconnected, this, &Backend::onDisconnected);
    connect(&m_webSocket, &QWebSocket::textMessageReceived, this, &Backend::onTextMessageReceived);
    m_uiTimer.setInterval(10); // 10 milliseconds ~= 100 FPS
    connect(&m_uiTimer, &QTimer::timeout, this, &Backend::telemetryUpdated);
    m_uiTimer.start();
}

// Getters
QString Backend::connectionStatus() const { return m_connectionStatus; }
double Backend::speed() const { return m_speed; }
double Backend::rpm() const { return m_rpm; }
double Backend::voltage() const { return m_voltage; }
double Backend::current() const { return m_current; }
double Backend::soc() const { return m_soc; }
double Backend::tempMotor() const { return m_tempMotor; }
double Backend::tempCVT() const { return m_tempCVT; }
double Backend::accX() const { return m_accX; }
double Backend::accY() const { return m_accY; }
double Backend::accZ() const { return m_accZ; }
double Backend::dpsX() const { return m_dpsX; }
double Backend::dpsY() const { return m_dpsY; }
double Backend::dpsZ() const { return m_dpsZ; }
double Backend::roll() const { return m_roll; }
double Backend::pitch() const { return m_pitch; }
double Backend::latitude() const { return m_latitude; }
double Backend::longitude() const { return m_longitude; }
double Backend::distance() const { return m_distance; }
double Backend::lapDistance() const { return m_lapDistance; }
int Backend::lapCount() const { return m_lapCount; }
double Backend::currentLapTime() const { return m_currentLapTime; }
double Backend::bestLapTime() const { return m_bestLapTime; }
double Backend::lastLapTime() const { return m_lastLapTime; }

void Backend::setConnectionStatus(const QString &status) {
    if (m_connectionStatus != status) {
        m_connectionStatus = status;
        emit connectionStatusChanged();
    }
}

void Backend::connectToServer(const QString &url) {
    setConnectionStatus("Connecting...");
    m_webSocket.open(QUrl(url));
}

void Backend::disconnectFromServer() { m_webSocket.close(); }
void Backend::onConnected() { setConnectionStatus("Connected"); }
void Backend::onDisconnected() { setConnectionStatus("Disconnected"); }

void Backend::onTextMessageReceived(const QString &message) {
    QJsonDocument doc = QJsonDocument::fromJson(message.toUtf8());
    if (!doc.isNull() && doc.isObject()) {
        QJsonObject obj = doc.object();
        
        m_speed = obj["speed"].toDouble();
        m_rpm = obj["rpm"].toDouble();
        m_voltage = obj["volt"].toDouble();
        m_current = obj["current"].toDouble();
        m_soc = obj["soc"].toDouble();
        m_tempMotor = obj["temperature"].toDouble();
        m_tempCVT = obj["temp_cvt"].toDouble();
        
        m_accX = obj["acc_x"].toDouble();
        m_accY = obj["acc_y"].toDouble();
        m_accZ = obj["acc_z"].toDouble();
        m_dpsX = obj["dps_x"].toDouble();
        m_dpsY = obj["dps_y"].toDouble();
        m_dpsZ = obj["dps_z"].toDouble();
        m_roll = obj["roll"].toDouble();
        m_pitch = obj["pitch"].toDouble();

        m_latitude = obj["latitude"].toDouble();
        m_longitude = obj["longitude"].toDouble();
        m_distance = obj["total_distance"].toDouble(); 
        m_lapDistance = obj["lap_distance"].toDouble();
        
        m_lapCount = obj["lap_count"].toInt();
        m_currentLapTime = obj["current_lap_time"].toDouble();
        m_bestLapTime = obj["best_lap_time"].toDouble();
        m_lastLapTime = obj["last_lap_time"].toDouble();

    }
}
