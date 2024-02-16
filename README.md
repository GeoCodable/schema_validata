# schema_validata

## Introduction
This library provides data validation functionalities for spreadsheets through validate_dataset(). It leverages a data dictionary (.xlsx) generated by build_data_dictionary and performs schema and custom regex pattern validation on your data sets.
A template [data_dictionary_template.xlsx](../data_dictionary_template.xlsx) is provided for reference and as a starting point for manually building the data dictionary. 

### Key Features:

  - Validate Schemas from Spreadsheets:
    - Define your data's expected structure (data types, lengths, ranges, etc.) in a user-friendly data dictionary (.xlsx) generated by the included build_data_dictionary tool. This dictionary acts as your single source of truth for data validation rules.
  - Custom Regex Validation:
    - Go beyond basic schema checks by defining custom regex patterns directly within the data dictionary. This allows you to tailor validation to your specific data requirements, ensuring compliance with unique data formats or constraints.
  - Detailed Reports:
    - Obtain detailed JSON reports summarizing the validation results, including identified errors and metadata for both your data and the data dictionary. These reports provide valuable insights into data quality issues.
  - Optional Excel Reports:
    - For easier human interpretation, convert JSON reports into user-friendly Excel reports with the schema_validation_to_xlsx tool. This can be helpful for sharing and presenting validation results with colleagues or stakeholders.

## Installation and import 
  - *pip install*:
    ``` cmd
    %pip install  git+https://github.com/ahamptonTIA/schema_validata.git
    ```
  - *Import*:
    ```python
    import schema_validata as sv

    ```
## General Workflow
### 1. Data Dictionary Creation:
  - Use *dataset_schema_to_xlsx* to generate a data dictionary (.xlsx) defining a dataset's actual schema. The provided data_dictionary_template.xlsx can also be used as a starting point.
Define custom regex patterns, ranges, lengths, nulls, and unique columns within the data dictionary.
### 2. Schema Mapping:
  - Create a *schema_mapping* dictionary manually, associating dataset names/tabs with corresponding sheets.tabs in the data dictionary.
### 3. Data Validation:
  - Run *validate_dataset* with the data dictionary, schema mapping, and your actual data set (.csv or .xlsx). It will generate a JSON file containing detailed validation results, including schema and regex validation errors.
### 4. Report Generation:
  - Use *schema_validation_to_xlsx* to convert the JSON results into a human-readable Excel report (.xlsx) for easier interpretation.

## Function Descriptions

### 1. dataset_schema_to_xlsx:

  - *Purpose*:
    - Analyzes a Pandas DataFrame to identify data types, null values, duplicates, unique values, allowed values, length, and potential value ranges for each column.  With an existing dataset, this can be a starting point for defining the data schema and generating a structured data dictionary (.xlsx) for validation processing as well as data goverance documentation.

  - *Parameters*:
    - df: The Pandas DataFrame to analyze.
    - out_dir: Output directory for the xlsx file.
    - out_name: Name for the xlsx data dictionary file.
      
  - *Output*:
    - The function returns the file path to an .xlsx data dictionary where each tab/sheet is a dataset schema.  This serves as a starign point for schema documenation if a dataset already exists. 

  - *Example*:
    ```python
    import schema_validata as sv
    
    
    file_path = 'C:\data\show_times_1.csv'
    
    # Generate a data dictionary (xlsx) given a CSV, XLSX, or XLS containing actual data
    data_dict_path = sv.dataset_schema_to_xlsx(file_path=file_path, 
                                              out_dir='C:\dataDictionary', 
                                              out_name='data_dictionary_template.xlsx'
                                              )
    ```
### 2. validate_dataset:

  - *Purpose*:
    - Performs data validation against a defined schema and custom regex patterns. It leverages a data dictionary created by build_data_dictionary to ensure that data conforms to expectations and business rules to improve data quality and reliability.
      
  - *Supported Checks*:
    - 'required_column' : required fields
    - 'data_type' : data type checks
    - 'allow_null' : missing value checks 
    - 'unique_value' : uniqeness/duplicates
    - 'length' : max string or value lengths 
    - 'range_min' :  minimum allowed value
    - 'range_mmx' :  maximum allowed value
    - 'allowed_value_list' : allowed values list
    - 'regex_pattern' : customized regex pattern checks
      
  - *Parameters*:
    - dataset_path: Path to the data set (.csv or .xlsx).
    - data_dict_path: Path to the data dictionary (.xlsx).
    - schema_mapping: Dictionary associating dataset names/tabs with data dictionary sections.
    - out_dir (optional): Output directory for JSON results.
    - out_name (optional): Name for the JSON output file.

  - *Output*:
    - JSON file containing:
      - Dataset metadata.
      - Data dictionary metadata.
      - Schema validation errors.
      - Row level value errors.


  - *Example*:

    ```python
    import schema_validata as sv
    
    # The path to the dataset file (CSV or Excel) to be validated.
    data_dict_path = 'C:\dataDictionary\data_dictionary_template.xlsx'
    
    #The path to the data dictionary file (CSV or Excel) containing schema and regex patterns.
    input_dataset = 'C:\data\show_times.xlsx'
    
    # A list of mappings between dataset names and corresponding data dictionary tab/sheet
    schema_mapping = [{'dataset': 'movies','data_dict': 'MOVIES_SCHEMA'},
                      {'dataset': 'theaters','data_dict': 'THEATERS_SCHEMA'}]
    
    
    json_string = sv.validate_dataset(  dataset_path=input_dataset, 
                                        data_dict_path=data_dict_path, 
                                        schema_mapping=schema_mapping,  
                                        list_errors=True,               # option to list out individual errors per row/value
                                        # out_dir=,                     # optional for saving an output .json file
                                        # out_name=,                    # optional for saving an output .json file
                                        ignore_errors=['allow_null']    # skip listing out every null record per row, provide overview counts only
                                    )
    ```

 
### 3. schema_validation_to_xlsx:

  - *Purpose*:
    - Geneartes a user-friendly excel spreadsheet (.xlsx) for interpretation and presentation of data validation results. It takes the JSON report generated by validate_dataset and converts it into a human-readable Excel spreadsheet.
      
  - *Parameters*:
    - validation_results: JSON output from validate_dataset.
    - out_dir (optional): Output directory for the xlsx file.
    - out_name (optional): Name for the xlsx file.

  - *Output*:
    - User-friendly Excel report (.xlsx) with tabs/sheets:
      - Metadata overview
        - Metadata for the data dictioanry file as well as the dataset to be validated.
      - Schema error summary
        - A single tab containing high level errors for each dataset to be validated.
      - Individual value error details by dataset name (if applicable).
      - A tab/sheet for each dataset listing value errors with row and lookup indexing. 

  - *Example*:
    
    ```python
        out_file = sv.schema_validation_to_xlsx(
                                                validation_results=json_string, 
                                                out_dir=r'C:\data', 
                                                out_name='show_time_validation')
    ```
