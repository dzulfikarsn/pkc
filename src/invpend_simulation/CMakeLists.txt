cmake_minimum_required(VERSION 3.10)
project(invpend_simulation)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
