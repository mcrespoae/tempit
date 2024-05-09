from setuptools import setup

setup(
    name="tempit",
    version="0.1.0",
    author="mcrespoae",
    author_email="info@mariocrespo.es",
    packages=["tempit"],
    description="A dead simple time decorator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mcrespoae/simple_tempit_decorator",
    install_requires=[],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
