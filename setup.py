import setuptools

# Load long description from local documentation
with open('readme.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='schema_validata',
    version='0.0.5',
    author='ahamptonTIA',
    description='data compliance validation utility for xlsx-defined schemas',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.11',
    py_modules=['schema_validata'],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    install_requires=[
        # Avoid forcing upgrades/downgrades for cluster pre-installed packages
        'numpy>=1.21.0,<2.0.0',      # Databricks 15.1+ ships numpy 1.21+
        'pandas>=2.1.4',             # Databricks 15.1+ ships pandas 2.1+
        'pyspark>=3.5.0',            # Databricks 15.1+ ships pyspark 3.5+
        'openpyxl>=3.1.0',           # Databricks 15.1+ ships openpyxl 3.1+
        'sqlglot',                   # Not pre-installed, safe to require
        'sql_metadata',              # Not pre-installed, safe to require
        'sqllineage',                # Not pre-installed, safe to require
        'pybind11>=2.12',            # Not pre-installed, safe to require
    ],
    include_package_data=True,
    zip_safe=False,
)
