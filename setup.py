import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='schema_validata',  # package name
    version='0.0.5',  # release version
    author='ahamptonTIA',  # author/org
    description=
        '''
        A comprehensive suite of validation functions to ensure dataset 
        compliance against Excel-based data dictionaries within 
        Databricks and Spark environments.
        ''',
    long_description=long_description,  # read from README.md
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],
    python_requires='>=3.10',  # DBR 15.1+ uses Python 3.10 or 3.11+
    py_modules=['schema_validata'],  # module name
    package_dir={'': 'src'},  # source directory
    packages=setuptools.find_packages(where="src"),  # all modules in src
    install_requires=[
        # Core data libraries: loose constraints for DBR compatibility
        'pandas>=1.5.0',
        'numpy>=1.21.0',
        # SQL parsing libraries: pinned to prevent breaking changes
        'sqlglot>=10.0.0,<24.0.0',
        'sqllineage>=1.4.0,<2.0.0',
        'sql_metadata>=0.1.0,<1.0.0',
        # File handling & utilities
        'openpyxl>=3.9.0,<4.0.0',
        'chardet>=5.0.0,<6.0.0',
        'python-dateutil>=2.8.2,<3.0.0',
    ]
)
