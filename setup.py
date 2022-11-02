from setuptools import setup, find_packages

setup(
    name="Phoenix-Framework",
    version="1.0",
    packages=find_packages(
        where="Phoenix-Framework",
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
            "pfserver = Phoenix-Framework.pfserver:main",
            "pfclient = Phoenix-Framework.pfclient:main"
        ]
    }
)
