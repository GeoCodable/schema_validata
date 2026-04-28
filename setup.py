import setuptools
import os

# Safe read for README.md to prevent installation-time crashes
long_description = "schema_validata package"
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as fh:
        long_description = fh.read()

setuptools.setup(
    name='schema_validata',
    version='0.0.6',                        # incremental version
    author='ahamptonTIA',
    description='Validation functions for dataset compliance based on an xlsx data dictionary.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    py_modules=['schema_validata'],         # Direct reference to src/schema_validata.py
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        # Core data libraries:
        # We ensure they exist, but use loose minimums so Pip accepts the 
        # pre-installed Databricks versions (including NumPy 2.x on newer Runtimes).
        'pandas>=1.5.0',
        # 'numpy>=1.23.2', 
        
        # SQL Tools: Versions compatible with Spark 3.5 (DBR 15) and Spark 4.0 (DBR 17+)
        'sqlglot>=23.0.0', 
        'sqllineage>=1.5.0',
        'sql-metadata>=2.0.0', 
        
        # File Handling & Utilities
        'openpyxl>=3.1.0',
        'chardet>=5.0.0',
        'python-dateutil>=2.8.2',
    ]
)
