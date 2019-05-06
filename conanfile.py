from conans import ConanFile, AutoToolsBuildEnvironment, tools
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
        os.unlink('ilmbase.tar.gz')

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        if "fPIC" in self.options.fields:
            env_build.fpic = self.options.fPIC
        config_dir = "{}/ilmbase-{}".format(self.source_folder, self.version)
        env_build.configure(configure_dir=config_dir)
        env_build.install()

    def package(self):
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/Half".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/Iex".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/IexMath".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/IlmThread".format(self.version), keep_path=False)
        self.copy("*.h", dst="include/OpenEXR", src="ilmbase-{}/Imath".format(self.version), keep_path=False)
        self.copy("IlmBaseConfig.h", dst="include/OpenEXR", src="config", keep_path=False)

        self.copy("*.lib", dst="lib", src=".", keep_path=False)
        self.copy("*.a", dst="lib", src=".", keep_path=False)
        self.copy("*.so", dst="lib", src=".", keep_path=False)
        self.copy("*.so.*", dst="lib", src=".", keep_path=False)
        self.copy("*.dylib*", dst="lib", src=".", keep_path=False)

        self.copy("*.dll", dst="bin", src="bin", keep_path=False)

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
