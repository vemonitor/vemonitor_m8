import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='vemonitor',
    version='0.0.1',
    description='Solar Plant Monitoring',
    url='https://github.com/vemonitor/vemonitor_m8',
    author='Eli Serra',
    author_email='eli.serra173@gmail.com',
    description='Simple image tools package. Used to convert, downscale or upscale images.',
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    license='Apache',
    packages=['tests', 'vemonitor'],
    install_requires=[
        'jsonschema',
        'pyyaml',
        'simplejson',
        'redis',
        'vedirect_m8',
        've_utils',
    ],
    extras_require={
        "TEST": [
            "pytest>=7.1.2",
            "coverage"
        ]
    },
    python_requires='>3.5.2',
    zip_safe=False
)
