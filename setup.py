from setuptools import setup

setup(
    name="simple_timeit_decorator",
    version="0.1.0",
    author="mcrespoae",
    author_email="info@mariocrespo.es",
    packages=["simple_timeit_decorator"],
    description="A dead simple time decorator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mcrespoae/simple_timeit_decorator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
