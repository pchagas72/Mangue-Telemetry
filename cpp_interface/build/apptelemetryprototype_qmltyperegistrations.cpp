/****************************************************************************
** Generated QML type registration code
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <QtQml/qqml.h>
#include <QtQml/qqmlmoduleregistration.h>

#if __has_include(<backend.h>)
#  include <backend.h>
#endif


#if !defined(QT_STATIC)
#define Q_QMLTYPE_EXPORT Q_DECL_EXPORT
#else
#define Q_QMLTYPE_EXPORT
#endif
Q_QMLTYPE_EXPORT void qml_register_types_Mangue_Telemetry()
{
    QT_WARNING_PUSH QT_WARNING_DISABLE_DEPRECATED
    qmlRegisterTypesAndRevisions<Backend>("Mangue.Telemetry", 1);
    QT_WARNING_POP
    qmlRegisterModule("Mangue.Telemetry", 1, 0);
}

static const QQmlModuleRegistration mangueTelemetryRegistration("Mangue.Telemetry", qml_register_types_Mangue_Telemetry);
