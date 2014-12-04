from setuptools import setup

setup(
    name='SB6',
    version='0.1',
    packages=['sb6'],
    package_dir = {'': 'src'},
    install_requires=[
        'Click',
    ],
    entry_points='''
        [gui_scripts]
        sb6_ex1=sb6.ex1:cli
    ''',
)
