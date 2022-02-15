load("//third_party:repo.bzl", "tf_http_archive")
load("//third_party/py:python_configure.bzl", "python_configure")

tf_http_archive(
    name = "pybind11",
    urls = [
        "https://mirror.bazel.build/github.com/pybind/pybind11/archive/v2.9.0.tar.gz",
        "https://github.com/pybind/pybind11/archive/v2.9.0.tar.gz",
    ],
    sha256 = "057fb68dafd972bc13afb855f3b0d8cf0fa1a78ef053e815d9af79be7ff567cb",
    strip_prefix = "pybind11-2.9.0",
    build_file = str("//third_party:pybind11.BUILD"),
)

python_configure(name = "local_config_python")