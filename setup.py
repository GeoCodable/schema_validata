import setuptools
import os

# Safe read for README.md
long_description = "schema_validata package"
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as fh:
        long_description = fh.read()

setuptools.setup(
    name='schema_validata',
    version='0.0.6',
    author='ahamptonTIA',
    description='Validation functions for dataset compliance.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.10',
    # Maps the 'src' folder to your package
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        # Core data libraries: Let DBR choose the best version
        'pandas>=1.5.0',
        'numpy>=1.23.2',  # Minimum for Python 3.11/3.12 support
        
        # SQL Tools: Using modern versions compatible with Spark 3.5/4.0
        'sqlglot>=23.0.0', 
        'sqllineage>=1.5.0',
        'sql-metadata>=2.0.0', # Corrected name and version
        
        # Utilities
        'openpyxl>=3.1.0',
        'python-dateutil>=2.8.2',
    ]
)
