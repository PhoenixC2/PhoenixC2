from setuptools import setup

setup(
    name="phoenixc2",
    version="1.0",
    author="Screamz2k",
    description="A C2 Framework for Red Team Operations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Screamz2k/PhoenixC2",
    license="BSD 3-Clause License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Pentesters",
        "License :: OSI Approved :: BSD 3-Clause License",
        "Programming Language :: Python :: 3",
    ],
    keywords="Red Team, C2, Pentesting",
    project_urls={
        "Documentation": "https://screamz2k.gitbook.io/phoenixc2/",
        "Source": "https://github.com/Screamz2k/PhoenixC2",
        "Tracker": "https://github.com/Screamz2k/PhoenixC2/issues",
    },
    include_package_data=True,
    install_requires=[
        "sqlalchemy==1.4.45",
        "flask",
        "rich",
        "pystyle",
        "psutil",
        "requests",
        "tomli",
        "tomli_w",
        "importlib-resources",
        "bleach",
        "markdown",
        "pyOpenSSL",
    ],
    extras_require={"dev": ["black", "isort", "ruff", "pre-commit"]},
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "phserver=phoenixc2.server.__main__:main",
            "phclient=phoenixc2.client.__main__:main",
        ]
    },
)
