from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

exts = [
    Extension(
        'sb6.app',
        sources=[
            'src/sb6/app.pyx',
            'src/sb6/sb6-c/sb6-c.cpp',
            'third_party/sb6/src/sb6/gl3w.c',
            'third_party/sb6/src/sb6/sb6.cpp',
            'third_party/sb6/src/sb6/sb6ktx.cpp',
            'third_party/sb6/src/sb6/sb6object.cpp',
            'third_party/sb6/src/sb6/sb6shader.cpp',
        ],
        include_dirs=['third_party/sb6/include', 'src/sb6/sb6-c'],
        libraries = ['glfw', ]
    )
]

setup(
    name='SB6',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['shaders/*.vert', 'shaders/*.frag']},
    ext_modules=cythonize(exts),
    install_requires=[
        'Click',
        'pyOpenGL',
    ],
    entry_points='''
        [gui_scripts]
        sb6_ex1=sb6.ex1:main
    ''',
)

