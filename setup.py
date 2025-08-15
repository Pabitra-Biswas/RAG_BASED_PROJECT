from setuptools import setup,find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    
    
setup(
    name='LLM_PROJECT',
    version='0.1',
    author='Pabitra Biswas',
    packages=find_packages(),
    install_requires=requirements,
)