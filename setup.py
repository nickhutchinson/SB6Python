from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
from functools import partial

SB6_ROOT = '/Users/Nick/Downloads/sb6code'

rooted = partial(os.path.join, SB6_ROOT)

exts = [
    Extension(
        'sb6.app',
        sources=([
            'src/sb6/app.pyx',
            'src/sb6/sb6-c.cpp',
        ] + map(rooted, [
            'src/sb6/gl3w.c',
            'src/sb6/sb6.cpp',
            'src/sb6/sb6ktx.cpp',
            'src/sb6/sb6object.cpp',
            'src/sb6/sb6shader.cpp', 
        ])),
        include_dirs=[os.path.join(SB6_ROOT, 'include')],
        libraries = ['glfw', ]
    )
]

setup(
    name='SB6',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    ext_modules=cythonize(exts),
    install_requires=[
        'Click',
    ],
    entry_points='''
        [gui_scripts]
        sb6_ex1=sb6.ex1:main
    ''',
)

