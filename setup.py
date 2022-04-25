from setuptools import setup, find_packages
from pathlib import Path


def read_long_description():
    with open(Path(__file__).parent / 'README.md', encoding='utf-8') as f:
        text = f.read()
    return text


install_requires = [
    "pillow>=9.0.0",
    "pysubs2>=1.0.0",
]

packages = find_packages()

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.9",
    "Typing :: Typed",
]

setup(
    name='utoolkit',
    version='0.0.1',
    description='toolkit for processing youtube files',
    long_description=read_long_description(),
    author='',
    author_email='',
    license='MIT',
    python_requires='>=3.9',
    packages=packages,
    install_requires=install_requires,
    package_data={
        'utoolkit': ['py.typed']
    },
    entry_points={
        'console_scripts': [
            'utoolkit=utoolkit.script:main',
        ],
    },
    classifiers=classifiers,
    zip_safe=False,
)
