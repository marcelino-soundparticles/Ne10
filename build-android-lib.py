#!/usr/bin/env python

import sys
import os
import subprocess
import platform
from pathlib import Path
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AndroidConfiguration:
    """ Fetch the current system Android configuration """
    android_sdk = None
    ndk_path = None
    cmake_path = None

    def __init__(self):
        home = os.path.expanduser("~")
        self.android_sdk = None
        if platform.system() == "Windows":
            self.android_sdk = os.path.join(home, Path('AppData/Local/Android/Sdk'))
        elif platform.system() == "Darwin":
            self.android_sdk = os.path.join(home, Path('Library/Android/sdk'))

        if self.android_sdk == None or not os.path.isdir(self.android_sdk):
            return

        ndk = os.path.join(self.android_sdk, "ndk")
        if not os.path.isdir(ndk):
            print("NDK not installed")
            return

        # Get the last ndk version
        self.ndk_path = sorted(Path(ndk).glob('*')).pop()

        cmake = os.path.join(self.android_sdk, "cmake")
        if not os.path.isdir(cmake):
            print("cmake not installed")
            return

        # Get the last cmake version
        self.cmake_path = sorted(Path(cmake).glob('*')).pop()


if __name__ == "__main__":

    androidConfig = AndroidConfiguration()
    #os.environ['ANDROID_NDK'] = str(androidConfig.ndk_path)

    archs = ['aarch64', 'arm']
    archs_flags = {
        'aarch64': "-DNE10_ENABLE_MATH=ON",
        'arm':  "-DNE10_ENABLE_MATH=ON"
    }
    for arch in archs:
        print(f"{bcolors.WARNING}Building arch {arch}")
        os.environ['NE10_ANDROID_TARGET_ARCH'] = arch
        Path(f"build.{arch}").mkdir(parents=True, exist_ok=True)
        result = subprocess.run([
            f"{androidConfig.cmake_path}/bin/cmake",
            f"-DANDROID_TOOLCHAIN_NAME={arch}-linux-android-33"
            f"-DANDROID_NDK={androidConfig.ndk_path}",
            f"-DCMAKE_TOOLCHAIN_FILE={androidConfig.ndk_path}/build/cmake/android.toolchain.cmake",
            "-DANDROID_ARM_NEON=ON",
            "-DCMAKE_MAKE_PROGRAM=/opt/homebrew/bin/ninja",
            "-DNE10_BUILD_EXAMPLES=ON",
            "-DNE10_BUILD_UNIT_TEST=OFF",
            "-DANDROID_DEMO=OFF",
            "-DNE10_ENABLE_IMGPROC=OFF",
            "-DNE10_ASM_OPTIMIZATION=OFF",
            "-DNE10_ENABLE_PHYSICS=OFF",
            archs_flags[arch],
            "-G Ninja",
            ".."
            ],
            cwd=f"build.{arch}"
        )
        if result.returncode != 0:
            exit(1)
        result = subprocess.run([
            "ninja"
            ],
            cwd=f"build.{arch}"
        )
        if result.returncode != 0:
            exit(1)
        result = subprocess.run([
            "ninja",
            "install"
            ],
            cwd=f"build.{arch}"
        )
        if result.returncode != 0:
            exit(1)
