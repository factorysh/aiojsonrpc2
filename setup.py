from setuptools import setup, find_packages

setup(
    name='aiojsonrpc2',
    version='0.1.0',
    description='',
    url='https://github.com/factorysh/aiojsonrpc2',
    install_requires=[
        'aiohttp',
        'json-rpc',
        'raven-aiohttp',
        'prometheus_client',
        'prometheus_async[aiohttp]',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
            'pytest-aiohttp',
        ],
    },
    licence="BSD",
    classifiers=[
      'Operating System :: MacOS',
      'Operating System :: POSIX',
      'License :: OSI Approved :: BSD',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
    ]
)

