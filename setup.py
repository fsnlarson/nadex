from setuptools import setup, find_packages

import nadex


def read(path):
    with open(path, 'rb') as f:
        return f.read().strip()


setup(
        name='nadex',
        version=nadex.__version__,
        description='Nadex API client',
        author='Kenji Noguchi',
        author_email='tokyo246@gmail.com',
        url='https://github.com/knoguchi/nadex',
        packages=find_packages(),
        scripts=['scripts/cancel-all-orders',
                 'scripts/create-order',
                 'scripts/get-contracts',
                 'scripts/get-orders',
                 'scripts/get-quote',
                 'scripts/get-balance',
                 'scripts/get-markets',
                 'scripts/get-positions',
                 'scripts/get-timeseries'
        ],
        install_requires=['requests'],
        test_suite='tests'
)
