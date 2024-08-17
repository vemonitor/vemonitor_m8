"""Vemonitor_m8 Setup"""
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='vemonitor_m8',
    version="0.0.5",
    description='Solar Plant Monitoring',
    url='https://github.com/vemonitor/vemonitor_m8',
    author='Eli Serra',
    author_email='eli.serra173@gmail.com',
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license='Apache',
    py_modules=[
        'vemonitor_m8.conf_manager.loader',
        'vemonitor_m8.conf_manager.schema_validate',
        'vemonitor_m8.conf_manager.schema_validate_selector',
        'vemonitor_m8.core.exceptions',
        'vemonitor_m8.core.utils',
        'vemonitor_m8.models.workers',
        'vemonitor_m8.models.item_dict'
    ],
    packages=[
        'test',
        'vemonitor_m8'
    ],
    package_dir={
        'vemonitor_m8': 'vemonitor_m8',
        'test': 'test'
    },
    package_data={
        'vemonitor_m8': [
            'conf_manager/confFiles/*.yaml',
            'conf_manager/confFiles/*.yml'
        ],
        'test': [
            'conf/*.yaml',
            'conf/*.yml'
        ]
    },
    include_package_data=True,
    install_requires=[
        'jsonschema>=4.23.0',
        'pyyaml>=6.0.2',
        'simplejson>=3.19.2',
        'redis>=5.0.8',
        'vedirect_m8>=1.3.2.4',
        've-utils>=2.5.3'
    ],
    extras_require={
        "TEST": [
            "pytest>=8.3.2",
            "pytest-cov>=5.0.0",
            "coverage>=7.6.1",
            "setuptools>=72.1.0",
            "twine>=5.1.1",
            "wheel>=0.44.0",
            "flake8>=7.1.1"
        ]
    },
    python_requires='>3.5.2',
    zip_safe=False
)
