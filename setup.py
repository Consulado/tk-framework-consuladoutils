import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tk-framework-consuladoutils",
    version="0.1.0",
    scripts=["tk-framework-consuladoutils"],
    author="Gabriel Valderramos",
    author_email="gabrielvalderramos@gmail.com",
    description="A Shotgun Framework package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/consulado/tk-framework-consuladoutils",
    packages=setuptools.find_packages(),
    package_data={"tk-framework-consuladoutils": ["icon_256.png", "*.yml"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
