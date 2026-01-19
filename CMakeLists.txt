# ==============================================================================
# AM32 FIRMWARE BUILD SYSTEM
# ==============================================================================
cmake_minimum_required(VERSION 3.20)

# Not buildable targets - should be skipped during build process
set(TARGET_SKIP_LIST)

# Release Skip List (Valid targets, but not for public release)
set(TARGET_RELEASE_SKIP_LIST)

include(cmake/manage_tools.cmake)

# 2. SUPERBUILD (CI / FULL RELEASE)
option(AM32_FULLBUILD "Build all architectures (ARM & RISC-V)" OFF)

if(AM32_FULLBUILD)
    project(AM32_SuperBuild NONE)
    include(ExternalProject)

    ExternalProject_Add(AM32_ARM
        SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}"
        BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/build_arm"
        CMAKE_ARGS "-DARCH=ARM" 
                   "-DCMAKE_TOOLCHAIN_FILE=${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/arm-none-eabi.cmake" 
                   "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
        INSTALL_COMMAND "" 
        USES_TERMINAL_CONFIGURE ON 
        USES_TERMINAL_BUILD ON
    )
    ExternalProject_Add(AM32_WCH_RISCV
         SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}"
         BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/build_wch_riscv"
         CMAKE_ARGS "-DARCH=WCH_RISCV" 
                    "-DCMAKE_TOOLCHAIN_FILE=${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/wch-riscv-none-embed.cmake" 
                    "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
         INSTALL_COMMAND "" 
         USES_TERMINAL_CONFIGURE ON 
         USES_TERMINAL_BUILD ON
     )
    return() 
endif()

# 3. TOOLCHAIN SELECTION
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    if(ARCH STREQUAL "ARM")
        set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/arm-none-eabi.cmake")
    elseif(ARCH STREQUAL "WCH_RISCV")
        set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/wch-riscv-none-embed.cmake")
    else()
        message(FATAL_ERROR "No ARCH specified! usage: cmake -DARCH=ARM (or WCH_RISCV) ..")
    endif()
endif()

# 4. PROJECT INITIALIZATION
project(AM32_${ARCH} C ASM)

# 5. MODULE LOADING
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")
include(VersionUtils)
include(TargetFactory)

message(STATUS "[${ARCH}] Configuring AM32 v${FIRMWARE_VERSION} (${FIRMWARE_GIT_HASH})")

# 6. LOAD TARGETS
if(ARCH STREQUAL "ARM")
    file(GLOB TARGETS "${CMAKE_SOURCE_DIR}/cmake/targets/arm/*.cmake")
elseif(ARCH STREQUAL "WCH_RISCV")
    file(GLOB TARGETS "${CMAKE_SOURCE_DIR}/cmake/targets/wch_riscv/*.cmake")
endif()

foreach(T ${TARGETS})
    message(STATUS "Loading Target: ${T}")
    include(${T})
endforeach()

# 7. IDE CONFIGURATION
include(VscodeGenerator)
am32_generate_launch_json()

message(STATUS "--- Configuration Complete ---")