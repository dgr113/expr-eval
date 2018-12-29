# coding: utf-8

from setuptools import setup, find_packages



setup(
    name='pandas_eval',
    version='0.3a',
    description='Safe pandas eval based on numexpr',
    long_description='Safe pandas eval based on numexpr',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'License :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Data Processing :: Data Eval :: Utility',
    ],
    keywords='Safe pandas eval based on numexpr',
    url='',
    author='dgr113',
    author_email='dmitry-gr87@yandex.ru',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
    ],
    include_package_data=True,
    zip_safe=False
)
