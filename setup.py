from setuptools import setup, find_packages

setup(
    name="trading",
    version="0.1.0",
    description="Trading algorithms",
    author="Marion Vasseur",
    keywords="trading",
    packages=find_packages(include=["trading"]),
    install_requires=[
        "python-binance==0.7.10",
        "numpy==1.20.2",
        "pandas==1.2.4",
    ],
)