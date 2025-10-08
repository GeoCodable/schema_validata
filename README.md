# schema_validata

## Introduction

**schema_validata** is a Python package for validating and profiling data in spreadsheets (CSV, XLSX) against a formal schema/data dictionary. It provides advanced data integrity checks using SQL-based rules. The package is designed primarily for the Databricks PySpark environment to validate schema and data integrity issues related to incoming files within data engineering, analytics, and data quality pipelines.

A template [data_dictionary_template.xlsx](../../blob/main/data_dictionary_template.xlsx) is provided for reference and as a starting point for building your own data dictionary.

---

## Key Features

- **Schema Validation**
  - Validate structure, types, nulls, uniqueness, allowed values, ranges, and regex patterns using a data dictionary (Excel).
  - Custom regular expression validation and detailed reporting of violations.

- **Automatic Data Profiling**
  - Generate a data dictionary from any data file with `dataset_schema_to_xlsx` or `dataset_schema_to_json`, inferring types, lengths, ranges, uniqueness, and more.

- **Detailed Reporting**
  - Obtain detailed JSON and Excel reports summarizing validation results, including row-level errors and metadata for both your data and the data dictionary.

- **Data Integrity Validation**
  - Define SQL-based integrity rules (e.g., cross-table checks, advanced business logic) in a dedicated `Data_Integrity` sheet of your data dictionary.
  - Run those rules on your datasets and get detailed and summary reports of violations.

---

## Installation

    pip install git+https://github.com/GeoCodable/schema_validata.git

#### Import

    import schema_validata as sv

---

## Workflow Overview

### 1. Data Dictionary Creation

- Use `dataset_schema_to_xlsx` to generate a data dictionary from any dataset (CSV, XLSX).
- Edit or expand the data dictionary using Excel, including custom regex, allowed values, min/max, etc.
- Optionally, add a `Data_Integrity` sheet for SQL-based integrity rules (see below).

### 2. Schema Mapping

- Create a schema mapping dictionary (Python list of dicts) associating each dataset/tab name with the corresponding data dictionary sheet/tab.

### 3. Data Validation

- Run `validate_dataset` with your data, data dictionary, and schema mapping.  
  Produces a JSON report (and optionally an Excel file) with:
    - Dataset and data dictionary metadata
    - Schema errors (types, nulls, uniqueness, etc)
    - Row-level value errors (optional, for detailed error tracing)

### 4. Data Integrity Validation (NEW)

- Add SQL rules to the `Data_Integrity` tab in your data dictionary (see example below).
- Use `data_integrity` to run these rules against your datasets, producing a dataframe of errors and a summary.

### 5. Report Generation

- Use `schema_validation_to_xlsx` to convert validation results into a human-readable Excel report.

---

## Function Reference & Examples

### 1. `dataset_schema_to_xlsx`

**Purpose:**  
Analyze a dataset and export a data dictionary (Excel) summarizing types, nulls, ranges, allowed values, etc.

    sv.dataset_schema_to_xlsx(
        file_path='data/my_file.csv',
        out_dir='schemas/',
        out_name='data_dictionary_template.xlsx'
    )

---

### 2. `validate_dataset`

**Purpose:**  
Validate a dataset against a data dictionary, including custom rules and regex patterns.

Supported checks:
- Required columns
- Data types
- Null/missing values
- Uniqueness/duplicates
- String length
- Numeric ranges
- Allowed value lists
- Regex patterns

**Example:**

    schema_mapping = [
        {'dataset': 'movies', 'data_dict': 'MOVIES_SCHEMA'},
        {'dataset': 'theaters', 'data_dict': 'THEATERS_SCHEMA'}
    ]

    results = sv.validate_dataset(
        dataset_path='data/data.xlsx',
        data_dict_path='schemas/data_dictionary_template.xlsx',
        schema_mapping=schema_mapping,
        list_errors=True,  # Include row-level details
        ignore_errors=['allow_null']
    )

---

### 3. `schema_validation_to_xlsx`

**Purpose:**  
Convert the JSON results of `validate_dataset` into an Excel report.

    sv.schema_validation_to_xlsx(
        validation_results=results,
        out_dir='reports/',
        out_name='validation_report'
    )

---

### 4. Data Integrity Validation (NEW)

#### SQL-Based Integrity Checks

**Define SQL rules in a Data Dictionary:**

The `Data_Integrity` sheet/tab in the data dictionary (Excel) should define:
- `Primary Table` - The table to refernece errors to
- `SQL Error Query` (the Spark SQL to run; should return violating rows)
- `Level` (e.g., "Error", "Warning")
- `Message` (description for the violation)

**Example Data_Integrity Sheet:**

    | Primary Table | SQL Error Query                             | Level  | Message              |
    |---------------|---------------------------------------------|--------|----------------------|
    | orders        | SELECT * FROM orders WHERE amount < 0       | Error  | Negative order amount|
    | customers     | SELECT * FROM customers WHERE email IS NULL | Warning| Missing email        |

**Run data integrity checks:**

    full_results, summary = sv.data_integrity(
        data_dict_path='schemas/data_dictionary_template.xlsx',
        csvs=['data/file1.csv', 'data/file2.csv']
    )

    print(summary)

- `full_results` is a DataFrame with detailed row-level violations.
- `summary` is a DataFrame summarizing issues by table, message, and severity.

---

## Utilities and Advanced Features

- **File and Table Management**:  
  Uses both Pandas, PySpark pandas, and spark SQL for distributed data.

- **Type Inference and Fixes**:  
  Utilities for inferring, fixing, and reporting types, nulls, encoding, and more.

- **Flexible Null/NA Handling**:  
  Customizable null value patterns and lists, including Excel and SQL-style nulls via the Config class.

- **Flexible Date/Time Handling**:  
  Customizable Date/Time patterns via the Config class.
---

## Links and References

- [Data dictionary template (Excel)](../../blob/main/data_dictionary_template.xlsx)
- [See full Python API: src/schema_validata.py](../../blob/main/src/schema_validata.py)

---

## Contributing

Contributions, bug reports, and suggestions are welcome! Please see the [issues](../../issues) page or submit a pull request.

---

## License

[MIT License](../../blob/main/LICENSE)
