from setuptools import find_packages, setup
setup(
    name='schoolware_api',
    packages=find_packages(include=['schoolware_api']),
    version='1.3.0',
    description='a schoolware api made in python',
    author='Maarten Buelens',
    license='MIT',
    install_requires=['requests>=2.25.1', 'playwright>=1.31.1'],
    author_email='schoolware_api@mb-server.com',
)
