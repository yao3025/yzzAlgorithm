# CMake 最低版本号要求
cmake_minimum_required(VERSION 3.10)

# 设置项目名称
project(yzzAlgorithm)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 添加算法子项目目录
add_subdirectory(01_KMP) 