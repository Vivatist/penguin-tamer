from setuptools import setup
setup(
    options={
        'package_data': {
            'penguin_tamer': ['*.yaml', 'locales/*.json'],
        },
    },
)