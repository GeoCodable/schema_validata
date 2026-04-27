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
        'programming language :: python :: 3',
        'programming language :: python :: 3.11',
        'license :: osi approved :: mit license',
        'operating system :: os independent',
        'topic :: scientific/engineering :: information analysis',
    ],
    # align with databricks runtime 15.1+ (python 3.11)
    python_requires='>=3.11',
    py_modules=['schema_validata'],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    install_requires=[
        # core dependencies aligned with dbr 15.1 system defaults
        # constraints prevent redundant overhead and ensure runtime compatibility
        'numpy>=1.25.2,<2.0.0',
        'pandas>=2.1.4',
        'pyspark>=3.5.0',
        'openpyxl>=3.1.0',
        'sqlglot',
        'sql_metadata',
        'sqllineage',
    ],
    include_package_data=True,
    zip_safe=False,
)
