import setuptools
from pathlib import Path

# Resolve the path to the README file using the directory of setup.py.
this_directory = Path(__file__).parent
readme_path = this_directory / "readme.md"

if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    # Fallback to uppercase README.md for case-sensitive environments.
    readme_upper_path = this_directory / "README.md"
    long_description = (
        readme_upper_path.read_text(encoding="utf-8")
        if readme_upper_path.exists()
        else "Data compliance validation utility for xlsx-defined schemas"
    )

setuptools.setup(
    name="schema_validata",
    version="0.0.6",
    author="ahamptonTIA",
    description="Data compliance validation utility for xlsx-defined schemas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.11",
    # Map the source directory for package discovery.
    package_dir={"": "src"},
    # Use 'packages' for directory structure with __init__.py.
    # Use 'py_modules' for a single module file, not both.
    packages=setuptools.find_packages(where="src"),
    # py_modules=["schema_validata"],  # Uncomment and remove 'packages' above if using a single file.
    install_requires=[
        # Pin numpy to <2.0.0 for ABI compatibility with Databricks Runtime.
        "numpy>=1.21.0,<2.0.0",
        # Pin pandas to <3.0.0 for Databricks Runtime compatibility.
        "pandas>=2.1.4,<3.0.0",
        # Match Databricks Runtime native Spark version.
        "pyspark>=3.5.0",
        # Standard dependencies for Excel and SQL processing.
        "openpyxl>=3.1.0",
        "sqlglot",
        "sql_metadata",
        "sqllineage",
        # If compiling C++ code, use pyproject.toml for build dependencies.
        # If runtime only, list here.
        "pybind11>=2.12",
    ],
    include_package_data=True,
    zip_safe=False,
)
