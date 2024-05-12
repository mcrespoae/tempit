from setuptools import setup

VERSION = "0.1.3"
setup(
    name="tempit",
    version=VERSION,
    author="mcrespoae",
    author_email="info@mariocrespo.es",
    packages=["tempit"],
    description="A dead simple time decorator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mcrespoae/tempit",
    install_requires=["joblib"],
    setup_requires=["joblib"],
    python_requires=">=3.8",
    keywords=["tempit", "time", "decorator", "performance", "concurrency", "parallel", "benchmark"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
