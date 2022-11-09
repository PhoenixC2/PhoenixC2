from setuptools import find_packages, setup

setup(
    name="Phoenix-Framework",
    version="1.0",
    author="Screamz2k",
    description="A C2 Framework for Red Team Operations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Screamz2k/Phoenix-Framework",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Pentesters",
        "License :: OSI Approved :: Apache License 2.0",
        "Programming Language :: Python :: 3",
    ],
    keywords="Red Team, C2, Pentesting",
    project_urls={
        "Documentation": "https://screamz2k.gitbook.io/phoenix-framework/",
        "Source": "https://github.com/Screamz2k/Phoenix-Framework",
        "Tracker": "https://github.com/Screamz2k/Phoenix-Framework/issues",
    },
    include_package_data=True,
    install_requires=[
        "sqlalchemy",
        "flask",
        "rich",
        "pystyle",
        "netifaces",
        "requests",
        "tomli",
        "tomli_w",
        "importlib-resources"
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "pylint"
        ]
    },
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pfserver=phoenix_framework.server.__main__:main",
            "pfclient=phoenix_framework.client.__main__:main",
        ]
    },
)
