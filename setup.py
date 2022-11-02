from setuptools import setup, find_packages

setup(
    name="Phoenix-Framework",
    version="1.0",
    packages=find_packages(
        where="phoenix-framework",
        exclude=["tests", "tests.*"]
    ),
    install_requires=[
        "sqlalchemy",
        "flask",
        "rich",
        "pystyle",
        "netifaces",
        "requests",
        "tomli",
        "tomli-w"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pfserver = phoenix-framework.pfserver:main",
            "pfclient = phoenix-framework.pfclient:main"
        ]
    }
)
