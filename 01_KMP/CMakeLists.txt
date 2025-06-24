# KMP 算法子项目 CMake 配置
cmake_minimum_required(VERSION 3.10)

# 设置子项目名称
project(KMP)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 添加可执行文件
add_executable(KMP main.cpp) 