# KMP 算法子项目 CMake 配置
cmake_minimum_required(VERSION 3.10)

# 设置子项目名称
project(KMP)

# 支持外部传入的自定义编译器路径
set(COMPILER_PATH "" CACHE FILEPATH "选择 C++ 编译器的路径")
if(COMPILER_PATH)
    set(CMAKE_CXX_COMPILER ${COMPILER_PATH} CACHE FILEPATH "使用的 C++ 编译器" FORCE)
endif()

# 支持外部传入的构建类型
set(BUILD_MODE "Release" CACHE STRING "构建类型选项: Debug, Release")
set(CMAKE_BUILD_TYPE ${BUILD_MODE} CACHE STRING "构建类型" FORCE)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 添加可执行文件
add_executable(KMP main.cpp)

# 支持 UTF-8 源文件编码
if(MSVC)
    target_compile_options(KMP PRIVATE /utf-8)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(KMP PRIVATE -finput-charset=UTF-8 -fexec-charset=UTF-8)
endif()

# 设置可执行文件输出目录，支持多配置生成器
set_target_properties(KMP PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}/Debug
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/Release
) 