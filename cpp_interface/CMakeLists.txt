cmake_minimum_required(VERSION 3.16)
project(TelemetryPrototype VERSION 0.1 LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ADD WebSockets here
find_package(Qt6 REQUIRED COMPONENTS Core Gui Qml Quick WebSockets Charts Widgets)
set(CMAKE_AUTOMOC ON)

qt_add_executable(appTelemetryPrototype src/main.cpp)

qt_add_qml_module(appTelemetryPrototype
    URI "Mangue.Telemetry"
    VERSION 1.0
    SOURCES
        src/backend.h
        src/backend.cpp
    QML_FILES 
        qml/main.qml
        qml/MainMenu.qml
        qml/TelemetryDash.qml
)

target_link_libraries(appTelemetryPrototype
    PRIVATE Qt6::Core Qt6::Gui Qt6::Qml Qt6::Quick Qt6::WebSockets Qt6::Charts Qt6::Widgets
)

target_include_directories(appTelemetryPrototype PRIVATE src)
