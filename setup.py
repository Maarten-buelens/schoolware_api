from setuptools import find_packages, setup
setup(
    name='schoolware_api',
    packages=find_packages(include=['schoolware_api']),
    version='0.0.5',
    description='a schoolware api made in python',
    author='Me',
    license='MIT',
    install_requires=['requests==2.25.1', 'playwright==1.31.1'],
)