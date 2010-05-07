#!/usr/bin/env python
from distutils.core import setup

setup(
    name='django-beanstalk',
    version='0.1',
    description='Django administration for beanstalk daemons',
    author='Alexandru Plugaru',
    author_email='alexandru.plugaru@gmail.com',
    url='http://github.com/humanfromearth/django-beanstalk',
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    packages=['django_beanstalk'],
    package_data={'django_beanstalk':['templates/admin/django_beanstalk/beanstalkdaemon/*.html']},
    requires=[
        'django (>=1.2)',
        'beanstalkc'
    ],
    zip_safe = True
)
