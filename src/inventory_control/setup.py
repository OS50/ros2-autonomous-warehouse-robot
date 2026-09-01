from setuptools import find_packages, setup

package_name = 'inventory_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros',
    maintainer_email='you@example.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'shelf_color_detector = inventory_control.shelf_color_detector:main',
            'motion_control = inventory_control.motion_control:main',
            'dashboard = inventory_control.dashboard:main',
        ],
    },
)