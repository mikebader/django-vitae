import setuptools

with open('README.rst', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='django-vitae',
    version='0.0.2',
    author='Michael Bader',
    author_email='michaeldmbader@gmail.com',
    description='A CV generator built for the Django web framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikebader/django-vitae',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.11',
        'markdown>=2.6.11',
        'citeproc-py>=0.4.0',
        'citeproc-py-styles>=0.1.1',
        'django-widgets>=-0.1.16'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ]
)
