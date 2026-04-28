import setuptools
import os

long_description = "A package for dataset schema validation in Databricks."
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as fh:
        long_description = fh.read()

setuptools.setup(
    name='schema_validata',
    version='0.0.5',
    author='ahamptonTIA',
    description='Check datasets for data compliance based on an xlsx data dictionary.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12', # For DBR 17.x+
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    # Maps the root package to the 'src' directory
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    # Allows 'import schema_validata' if the file is src/schema_validata.py
    py_modules=['schema_validata'] if os.path.exists('src/schema_validata.py') else [],
    install_requires=[
        # Databricks pre-installs these; >= ensures we don't force-downgrade them.
        'pandas>=1.5.3',
        'numpy>=1.23.5',
        
        # SQL processing - versions that support both NumPy 1.x and 2.x
        'sqlglot>=23.0.0',          
        'sqllineage>=1.5.0',        
        'sql_metadata>=0.1.0,<1.0.0',
        
        # Utilities
        'openpyxl>=3.1.0',          
        'chardet>=5.0.0',
        'python-dateutil>=2.8.2',
    ]
)
