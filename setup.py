from setuptools import setup, find_packages

setup(
    name="doodle-sdk",  # Replace with your package name
    version="0.1.0",
    description="SDK for better interfacing of Doodle Labs Radio",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Andrew Wilkins",
    author_email="andrew.wilkins@ascendengineer.com",
    url="https://github.com/afwilkin/doodle-sdk",
    license="",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",  # Add your dependencies here
    ],
    extras_require={
        "dev": [
            "mkdocs",
            "mkdocs-material",
            "pytest",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)