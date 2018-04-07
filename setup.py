#!/usr/bin/env python3

from setuptools import setup

setup(
    name="certbot-ovh",
    version="0.1",
    packages=['certbot_ovh'],
    install_requires=[
        'certbot>=0.23.0',
        'ovh>=0.4.8',
    ],
    entry_points={
        'certbot.plugins': [
            'dns = certbot_ovh.dns_ovh:Authenticator',
        ],
    },
    author="Vianney le Clément de Saint-Marcq",
    author_email="code@quartic.eu",
    description="OVH DNS authenticator plugin for certbot",
    url="https://github.com/vianney/certbot-ovh",
    license="Apache License 2.0",
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
