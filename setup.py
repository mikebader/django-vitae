import setuptools

def long_description():
    with open('README.rst', 'r') as f:
        return f.read()

setuptools.setup(
    name='django-vitae',
    version='0.1.0',
    author='Michael Bader',
    author_email='michaeldmbader@gmail.com',
    license='BSD Three Clause',
    description='A CV generator built for the Django web framework.',
    long_description=long_description(),
    url='https://github.com/mikebader/django-vitae',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.11',
        'markdown>=2.6.11',
        'citeproc-py>=0.4.0',
        'citeproc-py-styles>=0.1.1',
        'django-widgets>=-0.1.16',
        'django-widget-tweaks>=1.4.9',
        'reportlab>=3.6.3'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ]
)
