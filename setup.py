import setuptools

with open('README.rst', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='django-cv',
    version='0.0.2',
    author='Michael Bader',
    author_email='michaeldmbader@gmail.com',
    description='A CV generator built for the Django web framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikebader/django-cv',
    packages=setuptools.find_packages(),
    install_requires=[
        'markdown',
        'citeproc-py',
        'citeproc-py-styles',
        'django-widgets'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ]
)
