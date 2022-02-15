import os
import posixpath
import re
import shutil
import logging
import ast

from distutils import sysconfig
import setuptools
from setuptools.command import build_ext

HERE = os.path.dirname(os.path.abspath(__file__))


def _get_version():
    """Parse the version string from __init__.py."""
    version = 'unknown'
    with open('hnsw/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
    return version


class BazelExtension(setuptools.Extension):
    """A C/C++ extension that is defined as a Bazel BUILD target."""

    def __init__(self, name, bazel_target):
        self.bazel_target = bazel_target
        self.relpath, self.target_name = posixpath.relpath(bazel_target, "//").split(":")
        setuptools.Extension.__init__(self, name, sources=[])


class BuildBazelExtension(build_ext.build_ext):
    """A command that runs Bazel to build a C/C++ extension."""

    def run(self):
        for ext in self.extensions:
            self.bazel_build(ext)
        build_ext.build_ext.run(self)

    def bazel_build(self, ext):
        with open("WORKSPACE", "r") as f:
            workspace_contents = f.read()

        with open("WORKSPACE", "w") as f:
            f.write(
                re.sub(
                    r'(?<=path = ").*(?=",  # May be overwritten by setup\.py\.)',
                    sysconfig.get_python_inc().replace(os.path.sep, posixpath.sep),
                    workspace_contents,
                )
            )
        logging.info("ext.name is: " + ext.name)
        logging.info("build_temp directory is: " + self.build_temp)
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        bazel_argv = [
            "bazel",
            "build",
            ext.bazel_target,
            "--symlink_prefix=" + os.path.join(self.build_temp, "bazel-"),
            "--compilation_mode=" + ("dbg" if self.debug else "opt"),
        ]
        logging.info("bazel command is: " + str(bazel_argv))
        self.spawn(bazel_argv)

        shared_lib_ext = ".so"
        shared_lib = ext.name + shared_lib_ext
        ext_bazel_bin_path = os.path.join(self.build_temp, "bazel-bin", ext.relpath, shared_lib)
        logging.info("ext_bazel_bin_path is: " + ext_bazel_bin_path)
        ext_dest_path = self.get_ext_fullpath(ext.name)
        ext_dest_dir = os.path.dirname(ext_dest_path)
        logging.info("ext_dest_path is: " + ext_dest_path)
        logging.info("ext_dest_dir is: " + ext_dest_dir)

        if not os.path.exists(ext_dest_dir):
            os.makedirs(ext_dest_dir)
        shutil.copyfile(ext_bazel_bin_path, ext_dest_path)

        package_dir = os.path.join(ext_dest_dir, "hnsw")
        logging.info("package_dir is: " + package_dir)
        if not os.path.exists(package_dir):
            os.makedirs(package_dir)

        shutil.copyfile(
            "hnsw/__init__.py", os.path.join(package_dir, "__init__.py")
        )
        proto_file = "math.so"
        proto_bazel_bin_path = os.path.join(
            self.build_temp,
            "bazel-bin",
            "hnsw",
            proto_file
        )
        logging.info("proto_bazel_bin_path is: " + proto_bazel_bin_path)
        shutil.copyfile(proto_bazel_bin_path, os.path.join(package_dir, proto_file))


setuptools.setup(
    version=_get_version(),
    cmdclass=dict(build_ext=BuildBazelExtension),
    ext_modules=[
        BazelExtension("math", "//hnsw:math", )
    ]
)
