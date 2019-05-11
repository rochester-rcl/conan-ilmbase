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
    default_options = "shared=False", "namespace_versioning=True", "fPIC=False"

    def config_options(self):
        if self.settings.os == 'Windows':
            self.options.remove('fPIC')

    def configure(self):
        if "fPIC" in self.options.fields and self.options.shared:
            self.options.fPIC = True

    def source(self):
        tools.download(
            "https://github.com/openexr/openexr/releases/download/v{}/ilmbase-{}.tar.gz".format(self.version,
                                                                                                self.version),
            'ilmbase.tar.gz')
        tools.untargz('ilmbase.tar.gz')
        tools.replace_in_file("{}/ilmbase-{}/CMakeLists.txt".format(self.source_folder, self.version), "PROJECT ( ilmbase )",
                              """PROJECT ( ilmbase )
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set (CMAKE_CXX_STANDARD 11)""")

    def build(self):
        cmake = CMake(self)

        cmake.definitions.update(
            {"OPENEXR_BUILD_SHARED": True,
             "BUILD_ILMBASE_STATIC": True,
             "OPENEXR_VERSION": self.version,
             "OPENEXR_SOVERSION": self.version,
             })

        if "fPIC" in self.options.fields:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure(source_dir="{}/ilmbase-{}".format(self.source_folder, self.version))
        cmake.build(target="install")


    def package(self):
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/Half".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/Iex".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/IexMath".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/IlmThread".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/Imath".format(self.version), keep_path=False)
        self.copy("IlmBaseConfig.h", dst="include/OpenEXR", src="config", keep_path=False)
        self.copy("*.so", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.so.*", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.dylib*", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.dll", dst="bin", src="bin", keep_path=False)
        self.copy("*.a", dst="lib", src="package/lib", keep_path=False)
        self.copy("*.lib", dst="lib", src="package/lib", keep_path=False)

        self.copy("FindIlmBase.cmake", src=".", dst=".")
        self.copy("license*", dst="licenses", src="ilmbase-{}".format(self.version), ignore_case=True, keep_path=False)

    def package_info(self):
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")
        self.cpp_info.includedirs = ['include', 'include/OpenEXR']
        self.cpp_info.libs = ["Imath", "IexMath", "Half", "Iex",
                              "IlmThread"]
        if not self.settings.os == "Windows":
            self.cpp_info.cppflags = ["-pthread"]
