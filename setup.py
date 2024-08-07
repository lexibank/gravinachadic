from setuptools import setup, find_packages
import json

with open("metadata.json", encoding="utf-8") as fp:
    metadata = json.load(fp)

setup(
    name='lexibank_gravinachadic',
    py_modules=['lexibank_gravinachadic'],
    include_package_data=True,
    packages=find_packages(where="."),
    url=metadata.get("url",""),
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'gravinachadic=lexibank_gravinachadic:Dataset',
        ]
    },
    install_requires=[
        "pylexibank>=3.0.0",
        "lingpy"
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
