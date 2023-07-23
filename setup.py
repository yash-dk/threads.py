from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    version="0.0.2",
    name='threads-py-wrapper',
    description='Unofficial API for Threads by Instagram. With type hints.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yash-dk/threads.py',
    project_urls={
        'Issue Tracker': 'https://github.com/yash-dk/threads.py/issues',
        'Source Code': 'https://github.com/yash-dk/threads.py',
        'Download': 'https://github.com/yash-dk/threads.py/tags',
    },
    license='MIT',
    author='Yash Khadse',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)