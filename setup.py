from distutils.util import convert_path
from setuptools import find_packages, setup

module_name = "pydayz"
main_ns = {}
ver_path = convert_path(f"src/{module_name}/version.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name=module_name,
    version=main_ns["__version__"],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    license="MIT",
    description="Collection of DayZ bots, scripts and hacks",
    keywords=["DayZ", "bots", "hacks", "scripts"],
    long_description_content_type="text/markdown",
    long_description=open("README.md", encoding="utf8").read(),
    install_requires=["iocontroller"],
    url="https://github.com/tassoneroberto/py-dayz",
    author="Roberto Tassone",
    author_email="roberto.tassone@proton.me",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "pydayz_crack_passcode = pydayz.bots.crack_passcode:main",
        ],
    },
)
