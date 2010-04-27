#!/usr/bin/env python
from distutils.core import setup

setup(
    name='django-beanstalk',
    version='0.1',
    description='Django administration for beanstalk daemons',
    author='Alexandru Plugaru',
    author_email='alexandru.plugaru@gmail.com',
    url='http://github.com/humanfromearth/django-beanstalk',
    license='GPLv2',
    packages=['django_beanstalk'],
    install_requires=['beanstalkc'],
)
