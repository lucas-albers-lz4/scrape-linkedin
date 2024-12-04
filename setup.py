from setuptools import setup, find_packages

setup(
    name="linkedin-job-parser",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'selenium>=4.27.1',
        'beautifulsoup4>=4.12.0',
        'pytest>=8.3.3',
    ],
) 