# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name='Guguji',
    version='0.2',
    description='A python api for memobird guguji',
    packages=find_packages(),
    py_modules=['Guguji'],
    author='auzn',
    author_email='auzn.cn@gmail.com',
    url='https://github.com/auzn/Guguji',
    keywords='memobird guguji',
    install_requires=['requests', 'Pillow', 'imgkit'],
    license='MIT'
)
