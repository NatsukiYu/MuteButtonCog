from setuptools import setup, find_packages

with open('requirements.txt', 'r') as fp:
    requirements = fp.read().splitlines()

setup(
    name='MuteButtonCog',
    version='1.0.0',
    license='MIT',
    description='Physical mute button.',
    author='@natsuki__yu',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements,
)
