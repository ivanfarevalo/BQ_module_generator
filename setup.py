from setuptools import setup

setup(
    name='bqmod',
    version='0.1.0',
    py_modules=['bqmodule'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'bqmod = bqmodule:bqmod',
        ],
    },
)