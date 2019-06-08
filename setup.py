from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='python-throttle',
    packages=['limiter'],
    version='0.2.0',
    description='Super naive python redis limiter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='soulomoon',
    author_email='fwy996602672@gmail.com',
    url='https://github.com/soulomoon/python-throttle',
    keywords=['throttle limiter redis counter timer middleware'],
    python_requires='>=3.5',
    install_requires=[
        'redis>=3'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
