import setuptools
import os

# Safe read for README.md to prevent installation-time crashes
long_description = "schema_validata package"
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as fh:
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
        # DataBricks core utilities - Match all current Databricks ranges
        # NOTE: These are provided by Databricks runtimes and are commented out
        # to prevent version conflicts. The package will NOT modify them if already installed.
        # 'pyspark',    
        # 'pandas',    
        # 'numpy>=1.21.0,<2.2.0',       # Keep numpy from jumping to 2.4.4
        # 'packaging>=23.2.0,<25.0.0',  # Keep packaging from jumping to 26.2
        # 'Pygments>=2.15.0,<2.20.0',   # Keep the notebook UI stable
        # 'platformdirs<4.4.0',         # Prevent updates beyond 4.4
        
        # SQL parsing libraries - version constraints ensure compatibility
        'sqlglot>=10.0.0',                  # SQL parsing with Databricks dialect
        'sqllineage>=1.4.0',                # SQL lineage extraction (fallback parser)
        'sql_metadata>=1.0.0,<3.0.0',       # SQL metadata extraction utility
        
        # Excel file handling - compatible across all Databricks runtimes
        'openpyxl>=3.0.0',           # Compatible with all Databricks runtimes
        
        # Character encoding detection - optional but recommended
        'chardet>=4.0.0',            # Compatible with all Databricks runtimes
        
        # Date/time utilities
        'python-dateutil>=2.8.0',    # Robust date parsing across Python versions
    ]
)
