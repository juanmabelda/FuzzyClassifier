import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FuzzyTree", # Replace with your own username
    version="0.1",
    author="Juanma Belda",
    author_email="jmbeldalois@gmail.com",
    description="A Fuzzy Algorithm for classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://test.pypi.org/legacy/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)