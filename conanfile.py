from conans import ConanFile, CMake, tools

import os


# Based on https://github.com/karasusan/conan-ilmbase/blob/master/conanfile.py


class IlmBaseConan(ConanFile):
    name = "IlmBase"
    description = "IlmBase is a component of OpenEXR. OpenEXR is a high dynamic-range (HDR) " \
                  "image file format developed by Industrial Light & Magic for use in computer imaging applications."
    version = "2.3.0"
    license = "BSD"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "namespace_versioning": [True, False], "fPIC": [True, False]}
    requires = ("zlib/1.2.8@conan/stable")
    generators = "cmake"
    default_options = "shared=True", "namespace_versioning=True", "fPIC=False"

    def config_options(self):
        if self.settings.os == 'Windows':
            self.options.remove('fPIC')

    def configure(self):
        if "fPIC" in self.options.fields and self.options.shared:
            self.options.fPIC = True

    def source(self):
        # TODO use master branch of git because releases are no good with CMake
        self.run("git clone https://github.com/openexr/openexr.git openexr")
        tools.replace_in_file("{}/openexr/IlmBase/CMakeLists.txt".format(self.source_folder), "PROJECT(ilmbase VERSION ${ILMBASE_VERSION})",
                              """PROJECT(ilmbase VERSION ${ILMBASE_VERSION})
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set (CMAKE_CXX_STANDARD 11)""")

    def build(self):
        cmake = CMake(self)

        cmake.definitions.update(
            {"OPENEXR_BUILD_ILMBASE": True,
             "OPENEXR_BUILD_OPENEXR": False,
             "OPENEXR_BUILD_SHARED": self.options.shared,
             "OPENEXR_BUILD_STATIC": not self.options.shared,
             "OPENEXR_BUILD_PYTHON_LIBS": False,
             "OPENEXR_NAMESPACE_VERSIONING": False,
             "CMAKE_PREFIX_PATH": self.deps_cpp_info["zlib"].rootpath
             })

        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_dir="{}/openexr".format(self.source_folder))
        cmake.build(target="install")

    def package(self):
        self.copy("*.h", dst="include/OpenEXR", src="openexr/IlmBase/Half", keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="openexr/IlmBase/Iex".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="openexr/IlmBase/IexMath".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="openexr/IlmBase/IlmThread".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="openexr/IlmBase/Imath".format(self.version), keep_path=False)
        self.copy("IlmBaseConfig.h", dst="include/OpenEXR", src="config", keep_path=False)
        self.copy("*.so", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.so.*", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.dylib*", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.dll", dst="bin", src="bin", keep_path=False)
        self.copy("*.a", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.lib", dst="lib", src="package/lib", keep_path=False)

        self.copy("FindIlmBase.cmake", src=".", dst=".")
        self.copy("license*", dst="licenses", src="openexr".format(self.version), ignore_case=True, keep_path=False)

    def package_info(self):
        # TODO libs need to reflect namespace versioning
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")
        self.cpp_info.includedirs = ['include', 'include/OpenEXR']
        self.cpp_info.libs = ["Imath", "IexMath", "Half", "Iex",
                              "IlmThread"]
        if not self.settings.os == "Windows":
            self.cpp_info.cppflags = ["-pthread"]
