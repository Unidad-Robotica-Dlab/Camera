cmake_minimum_required(VERSION 3.12)
cmake_policy(SET CMP0074 NEW)
project(PFCameraLib_ConfigAndGrab_Console_OpenCV CXX)
#find_package(pfcTypes CONFIG REQUIRED)
if(NOT TARGET Photonfocus::PFCameraLib)
	find_package(PFBase CONFIG REQUIRED PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../../../)
endif()
set(OpenCV_STATIC OFF)
find_package(OpenCV REQUIRED)
message("-- Found OpenCV version: ${OpenCV_VERSION}")
message("-- OpenCV Include dirs: ${OpenCV_INCLUDE_DIRS}")

add_executable(PFCameraLib_ConfigAndGrab_Console_OpenCV ConfigAndGrab_Console_OpenCV.cpp)
#set_target_properties(PFCameraLib_ConfigAndGrab_Console_OpenCV PROPERTIES OUTPUT_NAME ConfigAndGrab_Console_OpenCV)
set_target_properties(PFCameraLib_ConfigAndGrab_Console_OpenCV PROPERTIES FOLDER PFCameraLib/Examples/C++)
target_include_directories(PFCameraLib_ConfigAndGrab_Console_OpenCV PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(PFCameraLib_ConfigAndGrab_Console_OpenCV PRIVATE Photonfocus::PFCameraLib ${OpenCV_LIBS})