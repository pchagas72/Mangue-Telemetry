# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "")
  file(REMOVE_RECURSE
  "CMakeFiles/appTelemetryPrototype_autogen.dir/AutogenUsed.txt"
  "CMakeFiles/appTelemetryPrototype_autogen.dir/ParseCache.txt"
  "appTelemetryPrototype_autogen"
  )
endif()
