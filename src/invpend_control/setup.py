from setuptools import find_packages, setup

import os
from glob import glob

package_name = 'invpend_control'
package_dir = os.path.dirname(os.path.abspath(__file__))


def relative_files(pattern):
    return [
        os.path.relpath(path)
        for path in glob(os.path.join(package_dir, pattern))
    ]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            relative_files(os.path.join('resource', package_name))),
        ('share/' + package_name,
            relative_files('package.xml')),
        (os.path.join('share', package_name, 'launch'), relative_files(
            os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config'), relative_files(
            os.path.join('config', '*.yaml')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jull',
    maintainer_email='elinsngawi@gmail.com',
    description='PID controller for the inverted pendulum (ros2_control effort interface)',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'pid_controller = invpend_control.pid_controller:main',
            'push_pole = invpend_control.push_pole:main',
        ],
    },
)
