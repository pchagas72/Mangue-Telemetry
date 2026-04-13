#pragma once
#include <QObject>
#include <QString>
#include <QtQml/qqml.h>
#include <QtWebSockets/QWebSocket>
#include <QJsonObject>
#include <QJsonDocument>
#include <qtimer.h>

class Backend : public QObject {
    Q_OBJECT
    QML_ELEMENT
    
    Q_PROPERTY(QString connectionStatus READ connectionStatus NOTIFY connectionStatusChanged)
    
    // Powertrain and battery
    Q_PROPERTY(double speed READ speed NOTIFY telemetryUpdated)
    Q_PROPERTY(double rpm READ rpm NOTIFY telemetryUpdated)
    Q_PROPERTY(double voltage READ voltage NOTIFY telemetryUpdated)
    Q_PROPERTY(double current READ current NOTIFY telemetryUpdated)
    Q_PROPERTY(double soc READ soc NOTIFY telemetryUpdated)
    
    // Temperatures
    Q_PROPERTY(double tempMotor READ tempMotor NOTIFY telemetryUpdated)
    Q_PROPERTY(double tempCVT READ tempCVT NOTIFY telemetryUpdated)

    // IMU (Accelerometer, Gyro, Orientation)
    Q_PROPERTY(double accX READ accX NOTIFY telemetryUpdated)
    Q_PROPERTY(double accY READ accY NOTIFY telemetryUpdated)
    Q_PROPERTY(double accZ READ accZ NOTIFY telemetryUpdated)
    Q_PROPERTY(double dpsX READ dpsX NOTIFY telemetryUpdated)
    Q_PROPERTY(double dpsY READ dpsY NOTIFY telemetryUpdated)
    Q_PROPERTY(double dpsZ READ dpsZ NOTIFY telemetryUpdated)
    Q_PROPERTY(double roll READ roll NOTIFY telemetryUpdated)
    Q_PROPERTY(double pitch READ pitch NOTIFY telemetryUpdated)

    // GPS data
    Q_PROPERTY(double latitude READ latitude NOTIFY telemetryUpdated)
    Q_PROPERTY(double longitude READ longitude NOTIFY telemetryUpdated)
    Q_PROPERTY(double distance READ distance NOTIFY telemetryUpdated)
    Q_PROPERTY(double lapDistance READ lapDistance NOTIFY telemetryUpdated)
    Q_PROPERTY(int lapCount READ lapCount NOTIFY telemetryUpdated)
    Q_PROPERTY(double currentLapTime READ currentLapTime NOTIFY telemetryUpdated)
    Q_PROPERTY(double bestLapTime READ bestLapTime NOTIFY telemetryUpdated)
    Q_PROPERTY(double lastLapTime READ lastLapTime NOTIFY telemetryUpdated)

public:
    explicit Backend(QObject *parent = nullptr);

    QString connectionStatus() const;
    double speed() const; double rpm() const; double voltage() const; double current() const; double soc() const;
    double tempMotor() const; double tempCVT() const;
    double accX() const; double accY() const; double accZ() const;
    double dpsX() const; double dpsY() const; double dpsZ() const;
    double roll() const; double pitch() const;
    double latitude() const; double longitude() const;
    double distance() const; double lapDistance() const;
    int lapCount() const; 
    double currentLapTime() const; double bestLapTime() const; double lastLapTime() const;

    Q_INVOKABLE void connectToServer(const QString &url);
    Q_INVOKABLE void disconnectFromServer();

signals:
    void connectionStatusChanged();
    void telemetryUpdated(); 

private slots:
    void onConnected();
    void onDisconnected();
    void onTextMessageReceived(const QString &message);

private:
    QWebSocket m_webSocket;
    QTimer m_uiTimer;
    QString m_connectionStatus;
    
    double m_speed, m_rpm, m_voltage, m_current, m_soc;
    double m_tempMotor, m_tempCVT;
    double m_accX, m_accY, m_accZ, m_dpsX, m_dpsY, m_dpsZ, m_roll, m_pitch;
    double m_latitude, m_longitude, m_distance, m_lapDistance;
    int m_lapCount;
    double m_currentLapTime, m_bestLapTime, m_lastLapTime;

    void setConnectionStatus(const QString &status);
};
