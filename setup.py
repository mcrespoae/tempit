from setuptools import setup

VERSION = "0.1.0"
setup(
    name="tempit",
    version=VERSION,
    author="mcrespoae",
    author_email="info@mariocrespo.es",
    packages=["tempit"],
    description="A dead simple time decorator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mcrespoae/simple_tempit_decorator",
    install_requires=[],
    python_requires=">=3.8",
    keywords=["tempit", "time", "decorator", "performance", "multithreading", "benchmark"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
