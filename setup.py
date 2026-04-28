import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='schema_validata',                 # name of the package
    version='0.0.5',                        # release version
    author='ahamptonTIA',                   # org/author
    description=\
        '''
        schema_validata

        The schema_validata package is a collection of functions
        to check datasets for data compliance based on a given xlsx
        data dictionary (see template).   
         
        ''',
    long_description=long_description,      # long description read from the the readme file
    long_description_content_type='text/markdown',
    classifiers=[                           # information to filter the project on PyPi website
                        'Programming Language :: Python :: 3',
                        'Programming Language :: Python :: 3.10',
                        'Programming Language :: Python :: 3.11',
                        'License :: OSI Approved :: MIT License',
                        'Operating System :: OS Independent',
                        'Natural Language :: English',
                        ],                                      
    python_requires='>=3.10,<4.0',          # Databricks Runtime 15.1+ supports Python 3.10+
    py_modules=['schema_validata'],         # name of the python package     
    package_dir={'':'src'},                 # directory of the source code of the package
    packages=setuptools.find_packages(where="src"), # list of all python modules to be installed

    install_requires=[
        # Core data libraries
        # We use >= to satisfy the pre-installed DBR versions without forcing a reinstall
        'pandas>=1.5.0',     
        'numpy>=1.21.0',     
        
        # SQL parsing
        'sqlglot>=10.0.0', 
        'sqllineage>=1.4.0,
        'sql_metadata>=0.1.0,
        
        # Utilities
        'openpyxl>=3.9.0,
        'chardet>=5.0.0,
        'python-dateutil>=2.8.2,
    ]
