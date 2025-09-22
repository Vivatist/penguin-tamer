from setuptools import setup
setup(
    options={
        'package_data': {
            'aiebash': ['*.yaml', 'locales/*.json'],
        },
    },
)