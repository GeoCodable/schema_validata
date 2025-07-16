import os                                   # Standard library for interacting with the operating system
import sys
import shutil                               # Standard library for high-level file operations
import json                                 # Standard library for working with JSON objects
import ast                                  # Standard library for parsing and processing Python abstract syntax trees
import math                                 # Standard library for mathematical functions
import hashlib                              # Standard library for generating hash values
import chardet                              # Library for character encoding detection
import re                                   # Standard library for regular expressions
import warnings                             # Standard library for issuing warning messages
from datetime import datetime               # Standard library for working with dates and times
from dateutil import parser as dt_parser    # Library for parsing dates from strings
import pandas as pd                         # Library for data manipulation and analysis
import numpy as np                          # Library for numerical operations
try:
    import pyspark
    import pyspark.pandas as ps             # Library for data manipulation and analysis with Spark
    import pyspark.sql.functions as F
    from pyspark.sql.types import IntegerType, FloatType, StringType, DateType, TimestampType, BooleanType
    from pyspark.sql import SparkSession
    pyspark_available = True

except ImportError:
    print("pyspark.pandas is not available in the session.")
    pyspark_available = False
from sqlite3 import connect                 # Standard library for creating and managing SQLite3 databases
import sqlparse                             # Library for parsing SQL queries
import sql_metadata                         # Library for advanced parsing of SQL queries
from sqllineage.runner import LineageRunner # More robust libary for itentifying sql parts

#---------------------------------------------------------------------------------- 

# List of warnings to silence
warnings_to_ignore = [
    {"category": UserWarning},
    {"message": "^Columns.*"},
    {"category": FutureWarning}
]

# Suppress the warnings
for warning in warnings_to_ignore:
    if "category" in warning:
        warnings.filterwarnings("ignore", category=warning["category"])
    elif "message" in warning:
        warnings.filterwarnings("ignore", message=warning["message"])
try:
    # Ignore future warning on silent down casting (code assumes new method)
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
    
#---------------------------------------------------------------------------------- 

# Config class
class Config:
    """
    Configuration class for storing package constants and settings.

    This class provides a central location for managing configuration settings
    and constants used throughout the schema_validata package.

    Attributes:
        NA_VALUES (list): List of strings representing values to be treated as NaN.
        NA_PATTERNS (list): List of regex patterns for identifying values to be treated as NaN.
        DATE_FORMAT (str): Default date format used for parsing dates in the application.
        ...
    Example:
        config/DATA_DICT_PRIMARY_KEY = 'Name' # Changing a configuration attribute 
        print(config.NA_VALUES)  # Accessing a configuration attribute
    """


    if pyspark_available:
        USE_PYSPARK = True
        SPARK_SESSION = SparkSession.builder.appName("schema_validata").getOrCreate()

    # Data dictionary schema
    DATA_DICT_SCHEMA = {
        "field_name": "object",
        "required": "object",
        "data_type": "object",
        "allow_null": "object",
        "length": "int",
        "range_min": "float",
        "range_max": "float",
        "regex_pattern": "object",
        "unique_value": "object",
        "allowed_value_list": "object"
    }


    # Data integrity schema
    DATA_INTEGRITY_SCHEMA = {	
	'Primary Table': "object",
	'SQL Error Query': "object",
	'Level': "object",
	'Message': "object"
    }	    

    # Data dictionary schema primary key field
    DATA_DICT_PRIMARY_KEY = "field_name"

    # Overview error message string formats
    SCHEMA_ERROR_TEMPLATES = {
        'required_column'       : "Column by name '{col}' is required, but missing in dataset.",  
        'optional_column'       : "Column by name '{col}' is missing in the dataset, but is optional.",  
        'allow_null'            : "Column '{col}' data has {count} null values, null values are not allowed.",
        'data_type'             : "Column '{col}' data type: {observed} does not match the required data type: {expected} .", 
        'unique_value'          : "Column '{col}' values must be unique. Found  {count} duplicate values in dataset column .",
        'length'                : "Column '{col}' max string  of: {observed} exceeds the max allowed  of: {expected} .",
        'range_min'             : "Column '{col}' min value of: {observed} is less than the minimum allowed value of: {expected} .",
        'range_max'             : "Column '{col}' max value of: {observed} exceeds the maximum allowed value of: {expected} .",
        'allowed_value_list'    : "Column '{col}' contains values that are not allowed: {err_vals} .",
        'regex_pattern'         : "Column '{col}' contains values which do not match the allowed format/pattern ."
    }

    # Overview error message string formats
    SCHEMA_REQUIRED_MESSAGE_LEVELS = {
        True    : "Error",  
        False   : "Informational/Warning",  
    }

    # Common US & ISO timestamp formats
    COMMON_TIMESTAMPS = [
                        # Common US Formats - Time 
                        "%I:%M:%S %p", # 12-Hour Time to seconds with AM/PM (Very Common)
                        "%I:%M:%S%p",  # 12-Hour Time to seconds with AM/PM (Common)
                        "%I:%M %p",    # 12-Hour Time to mins with AM/PM (Very Common)
                        "%I:%M%p",     # 12-Hour Time to mins with AM/PM (Common)
                        # Common International and ISO Standard Date Formats (ISO 8601)
                        "%H:%M:%S",    # 24-Hour Time (24-hour clock, US Military, Technical)
                        "%H:%M:%S %p"  # 24-Hour Time with AM/PM
                        ]

    # Common US & ISO date/datetime formats
    COMMON_DATETIMES = [
       
                        # US Formats - Date

                        "%m/%d/%Y",    # Month/Day/Year (Most Common)
                        "%d/%m/%Y",    # Day/Month/Year (Common)
                        "%b-%d-%Y",    # Month Abbreviation-Day-Year (e.g., Jan-01-2024)
                        "%B %d, %Y",   # Month Name-Day, Year (e.g., January 01, 2024)
                        "%Y-%m-%d",    # Year-Month-Day (ISO 8601 & Increasingly Common in US)
                        "%d-%m-%Y",    # Day-Month-Year (Less Common)

                        # US Date Time Formats 
                        "%m/%d/%Y %H:%M:%S", # Date and Time with Separators (Common)
                        "%Y-%m-%d %H:%M:%S", # Date and Time with Separators (Less Common)
                        "%d-%m-%Y %H:%M:%S", # Date and Time with Separators (Uncommon)

                        # ISO Standard Date Formats (ISO 8601)
                        #"%Y-%m-%d", # Year-Month-Day (Standard, Consistent) used above
                        "%Y-%m",   # Year-Month (Less Common)

                        # ISO Standard Date Time Formats (ISO 8601)
                        "%Y-%m-%dT%H:%M:%SZ", # Combined Date and Time with Zulu Time (Specific Use Cases)
                        "%Y-%m-%dT%H:%M:%S%z", # Combined Date and Time with Offset (Rare)
                        ]

    if pd.__version__ >= '1.5':
	    NA_VALUES = [
	        '#N/A N/A',  # Less standard combination
	        '-1.#IND',   # Specific float representation
	        '-1.#QNAN',  # Specific float representation
	        '1.#IND',    # Specific float representation
	        '1.#QNAN',   # Specific float representation
	        '<NA>',      # While pandas uses pd.NA, this string might not be default
	        'NULL',      # Uppercase NULL
	        'Null',      # Capitalized Null
	        '#REF!'      # Excel error
	    ]
    else:
	    NA_VALUES = [
	        '',          # Empty string
	        ' ',         # Single space
	        '#N/A',      # Excel error
	        '#N/A N/A',  # Less standard combination
	        '#NA',       # Excel error
	        '-1.#IND',   # Specific float representation
	        '-1.#QNAN',  # Specific float representation
	        '-NaN',      # Negative NaN
	        '-nan',      # Negative NaN (lowercase)
	        '1.#IND',    # Specific float representation
	        '1.#QNAN',   # Specific float representation
	        '<NA>',      # While pandas uses pd.NA, this string might not be default
	        'N/A',       # Common representation of missing values
	        'NA',        # Common representation of missing values
	        'NULL',      # Uppercase NULL
	        'NaN',       # Not a Number
	        'n/a',       # Lowercase n/a
	        'nan',       # Lowercase nan
	        'null',      # Lowercase null
	        'Null',      # Capitalized Null
	        '#REF!',     # Excel error
	        np.nan,      # NumPy NaN
	        None,        # Python None
	        'None'       # String None
	    ]

    # Standard pattern reps for nulls, values will be converted to nulls
    NA_PATTERNS = [
		    r'(?i)^\s*NOT\s{0,1}(?:\s|_|-|/|\\|/){1}\s{0,1}AVAILABLE\s*$',
		    r'(?i)^\s*N\s{0,1}(?:\s|_|-|/|\\|/){1}\s{0,1}A\s*$',
		    r'(?i)^\s*(?:\s|_|-|/|\\|/){1}\s*$',
		    r'^\s+$'
		    ]

    class jsonEncoder(json.JSONEncoder):
        """Custom JSON encoder class that handles serialization of NumPy data types
        (int64, float64, and arrays) for compatibility with JSON.

        This class inherits from `json.JSONEncoder` and overrides the `default` method
        to provide custom logic for serializing specific object types.
        """

        def default(self, obj):
            """
            Overrides the default method of JSONEncoder to handle specific object types.

            Parameters
            ----------
            obj: 
                The object to be serialized.
            Returns
            -------
                A JSON-serializable representation of the object.
            """
            if isinstance(obj, np.integer):
                """Handle NumPy integer types (e.g., int64) by converting them to regular Python int."""
                return int(obj)
            elif isinstance(obj, np.floating):
                """Handle NumPy floating-point types (e.g., float64) by converting them to regular Python float."""
                return float(obj)
            elif isinstance(obj, np.ndarray):
                """Handle NumPy arrays by converting them to lists for JSON encoding."""
                return self.encode(obj.tolist())  # Recursively convert to list
            return super().default(obj)

#---------------------------------------------------------------------------------- 

def db_path_to_local(path):
    """Function returns a local os file path from dbfs file path
    Parameters
    ----------
    path : str
        DataBricks dbfs file storage path
    Returns
    ----------
    file path: str
        local os file path
    """    
    if path.startswith(r'/mnt'):
        path = f"{r'/dbfs'}{path}"
    return re.sub(r'^(dbfs:)', r'/dbfs', path)

#----------------------------------------------------------------------------------    

def to_dbfs_path(path):
    """Function converts a local os file path to a dbfs file path
    Parameters
    ----------
    path : str
        local os file path
    Returns
    ----------
    file path: str
        DataBricks dbfs file storage path
    """        
    if path.startswith(r'/mnt'):
        path = f"{r'dbfs:'}{path}" 
    if not path.startswith(r'/Volumes') and path.startswith(r'/dbfs'):
        path = re.sub(r'^(/dbfs)', r'dbfs:', path)         
    return path 

#----------------------------------------------------------------------------------    

def get_byte_units(size_bytes):
    """Converts bytes into the largest possible unit of measure.

    Parameters
    ----------
    size_bytes : int
        Numeric value representing bytes.

    Returns
    -------
    str
        String representing the value and the largest unit size.
        Example: '200 : GB'
    """
    if size_bytes == 0:
        return '0 : B'

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1000)))
    p = math.pow(1000, i)
    s = round(size_bytes / p, 2)

    return f'{s} : {size_name[i]}'

# ----------------------------------------------------------------------------------

def get_md5_hash(file_path):
    """Generates an MD5 hash for the contents of a 
    files contents.

    Parameters
    ----------
    file_path : str
        Path to the file.

    Returns
    -------
    str
        MD5 hash string.
    """

    try:
        with open(file_path, "rb") as file:
            file_hash = hashlib.md5()
            while True:
                chunk = file.read(8192)
                if not chunk:
                    break
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except PermissionError:
        return f"Permission error reading file: {file_path}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# ----------------------------------------------------------------------------------

def get_spreadsheet_metadata(file_path):
    """Returns a dictionary with general metadata for a CSV or Excel file.

    Parameters
    ----------
    file_path : str
        Path to the CSV or Excel file.

    Returns
    -------
    dict
        Dictionary of file metadata.
    """
    try:
        # Extract filename and extension
        filename = os.path.basename(file_path)
        base_name, ext = os.path.splitext(filename)

        # Get date time file metadata
        statinfo = os.stat(file_path)
        create_date = datetime.fromtimestamp(statinfo.st_ctime).isoformat()
        modified_date = datetime.fromtimestamp(statinfo.st_mtime).isoformat()

        # Create dictionary to store the metadata
        file_meta = {}

        # Read the data into a pandas dataframe by sheet
        dfs = read_csv_or_excel_to_df(file_path, infer=True, multi_sheets=True)

        file_hash = get_md5_hash(file_path)
        for sheet_name, df in dfs.items():
            # if 'pyspark.pandas.frame.DataFrame' in str(type(df)):
            #     df = df.to_pandas()
            meta = {
                'file_path': file_path,
                'file_name': filename,
                'file_type': ext,
                'file_size_bytes': f'{statinfo.st_size:,}',
                'file_size_memory_unit': get_byte_units(int(statinfo.st_size)),
                'record_qty': f'{len(df):,}',
                'column_qty': f'{len(df.columns):,}',
                'file_md5_hash': file_hash,
                'created': create_date,
                'modified': modified_date
            }

            # Generate the schema dictionary
            file_meta[sheet_name] = meta

        return file_meta

    except FileNotFoundError:
        return f"File not found: {file_path}"
    except PermissionError:
        return f"Permission error reading file: {file_path}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# ----------------------------------------------------------------------------------
def is_numeric_type(value):
    """
    Checks if a value is a common numeric data type in 
    pandas, NumPy, or Python.

    Parameters:
    ----------
        value: The value to check.
    Returns:
    -------
        bool: True if the value is numeric, False otherwise.
    """
    return isinstance(value, (int, float, complex)) or np.issubdtype(type(value), np.number)

# ----------------------------------------------------------------------------------

def downcast_ints(value):
    """
    Downcast a numeric value to an integer if it is equal to 
    a float representation.
    
    Parameters
    ----------
    value: The numeric value to downcast.
    
    Returns
    -------
    The value as an integer if it is equal to its float 
    representation, otherwise the original value.
    """
    try:
        if isinstance(value, float) and int(value) == float(value):
            return int(value)
    except ValueError:
        pass
    return value

# ----------------------------------------------------------------------------------

def get_best_uid_column(df, preferred_column=None):
    """
    Identifies the column with the most unique values (excluding nulls) in a DataFrame.
    Supports pandas, Spark, and spark.pandas DataFrames.

    Parameters:
    -----------
    df : pandas.DataFrame or pyspark.sql.DataFrame or pyspark.pandas.DataFrame
        The input DataFrame.
    preferred_column : str, optional
        The preferred column if ties for uniqueness occur.

    Returns:
    --------
    str or None
        The column name with the most unique values, or None if none qualify.

    Raises:
    -------
    ValueError
        If `df` is not a pandas, Spark, or spark.pandas DataFrame.
    """
    is_pandas = isinstance(df, pd.DataFrame)
    is_spark_pandas = 'pyspark.pandas.frame.DataFrame' in str(type(df))

    if not (is_pandas or is_spark_pandas):
        raise ValueError("Input must be a pandas or spark.pandas DataFrame.")

    uniq_cnts = {}
    uid_dtypes = ['Integer', 'String']
    for col in df.columns:
        if 'pyspark.pandas.series.Series' in str(type(df[col])):
            _s = df[col].to_pandas()
        else:
            _s = df[col]

        if infer_data_types(_s) in uid_dtypes:
            unique_vals = _s.dropna().nunique()
            uniq_cnts[col] = int(unique_vals)

    if uniq_cnts:
        max_value = max(uniq_cnts.values())
        uid_cols = [c for c, uc in uniq_cnts.items() if uc > 0 and uc == max_value]
    else:
        return preferred_column

    if uid_cols:
        if preferred_column:
            uid_cols = [c for c in uid_cols if uniq_cnts[c] > uniq_cnts[preferred_column]]
        if not uid_cols:
            return preferred_column
        return uid_cols[0]
    else:
        return preferred_column
    
# ----------------------------------------------------------------------------------

def eval_nested_string_literals(data):
    """
    Iterates through a nested dictionary or JSON object, attempting to evaluate
    string representations of data types (e.g., lists, dict, tuples) into their 
    actual Python counterparts. Modifies the structure in-place, replacing string
    representations with evaluated values.

    Parameters:
    -----------
    data : dict or str
        The nested dictionary to iterate through, or a JSON string to be parsed.

    Returns:
    --------
    dict
        The modified dictionary with string representations replaced by evaluated
        values.

    Raises:
    -------
    ValueError
        If the provided data is not a valid JSON string.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

    for key, value in data.items():
        if isinstance(value, dict):
            eval_nested_string_literals(value)
        else:
            try:
                value = value.strip('"\'')
            except AttributeError:
                pass

            try:
                evaluated_value = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                evaluated_value = value

            if value != evaluated_value:
                data[key] = evaluated_value

    return data

# ----------------------------------------------------------------------------------
def remove_pd_df_newlines(df, replace_char=''):
    """
    Removes newline characters ('\n') from all string 
    columns in a pandas or pyspark.pandas DataFrame with the given replace 
    character.

    Parameters:
    -----------
    df : pandas.DataFrame or pyspark.pandas.DataFrame
        The DataFrame to process.
    replace_char : str, optional
        String value to replace newline character with.
        Defaults to single space (' ').

    Returns:
    --------
    pandas.DataFrame or pyspark.pandas.DataFrame
        The DataFrame with newlines removed from string columns.
    """
    # if isinstance(df, ps.DataFrame):
    #     return df.replace('\n', replace_char, regex=True)
    return df.replace('\n', replace_char, regex=True)

# ----------------------------------------------------------------------------------

def column_is_timestamp(df, column_name, time_format):
    """
    Checks if all non-null values in a DataFrame 
    column can be parsed as time-only given a 
    specific format.

    Parameters:
    -----------
    df : pandas.DataFrame or pyspark.pandas.DataFrame
        The DataFrame containing the column.
    column_name : str
        The name of the column to check.
    time_format : str
        The expected string time format.

    Returns:
    --------
    bool
        True if all non-null values in the column can 
        be parsed as time, False otherwise.
    """
    if 'pyspark.pandas.frame.DataFrame' in str(type(df)):
        df = df.to_pandas()
    column_as_str = df[column_name].astype(str).replace(r'^\s+$', pd.NA, regex=True).dropna()
    
    if len(column_as_str) == 0:
        return False
        
    def try_parse(time_str):
        try:
            if not isinstance(time_str, str):
                return False
            datetime.strptime(time_str, time_format).time()
            return True
        except ValueError:
            return False

    return column_as_str.apply(try_parse).all()

# ----------------------------------------------------------------------------------

def infer_datetime_column(df, column_name):
    """
    Attempts to convert a pandas or pyspark.pandas column to datetime 
    type, handling various formats. Integer columns 
    will not be attempted.

    Parameters:
    -----------
    df : pandas.DataFrame or pyspark.pandas.DataFrame
        The DataFrame containing the column.
    column_name : str
        The name of the column to convert.

    Returns:
    --------
    pandas.Series or pyspark.pandas.Series
        The column/series converted to a datetime type if successful,
        otherwise the unaltered column is returned.
    """
    is_spark_pandas = 'pyspark.pandas.frame.DataFrame' in str(type(df))
    _s = df[column_name].to_pandas() if is_spark_pandas else df[column_name]
    orig_series = _s.copy()

    string_column = _s.astype(str).replace(r'^\s+$', pd.NA, regex=True).dropna()
    if len(string_column) == 0:
        return df[column_name] if is_spark_pandas else orig_series

    if pd.api.types.is_string_dtype(string_column):
        try:
            if pd.api.types.is_integer_dtype(pd.to_numeric(string_column)):
                return df[column_name] if is_spark_pandas else orig_series
        except:
            if all(column_is_timestamp(df, column_name, ts_format) for ts_format in Config.COMMON_TIMESTAMPS):
                return df[column_name] if is_spark_pandas else orig_series

            for date_format in Config.COMMON_DATETIMES:
                try:
                    converted_series = pd.to_datetime(string_column, format=date_format)
                    return ps.Series(converted_series) if is_spark_pandas else converted_series
                except:
                    pass

            try:
                converted_series = orig_series.apply(dt_parser.parse)
                return ps.Series(converted_series) if is_spark_pandas else converted_series
            except:
                pass

    return df[column_name] if is_spark_pandas else orig_series

# ----------------------------------------------------------------------------------

def detect_file_encoding(file_path):
    """Detects the character encoding of a text-based file using chardet library.

    This function is useful for determining the appropriate encoding when reading
    files that may not explicitly declare their encoding. It analyzes a sample
    of the file's content to identify the most likely character encoding scheme
    used.

    Parameters:
    ----------
    file_path (str):
        The path to the target file.
    Returns:
    ----------
    str:
        The detected character encoding of the file. If chardet cannot
        determine the encoding with sufficient confidence (less than 50%),
        the function returns the pandas default encoding=None or ('utf-8') 
        as a default fallback.
    Raises:
    ----------
    OSError:
        If the specified file cannot be opened for reading.
    """

    try:
        with open(file_path, 'rb') as f:
            rawdata = f.read()
    except OSError as e:
        raise OSError(f"Error opening file: {file_path}. {e}")

    result = chardet.detect(rawdata)

    if result['confidence'] > 0.5:
        return result['encoding']
    else:
        print(f"Encoding confidence for '{file_path}' is low (< 50%). Using pandas default.")
        return None


#----------------------------------------------------------------------------------   
def read_spreadsheets(file_path, 
                      sheet_name=None, 
                      dtype=None, 
                      rm_newlines=True,
                      replace_char="", 
                      na_values=None
                      ):
    """
    Reads and processes raw data from Excel (.xlsx, .xls) or CSV (.csv) files 
    into a pandas DataFrame accounting for newline/return characters and datatypes. 
    Parameters:
    ----------
    file_path (str): 
        The path to the data file.
    sheet_name (str, optional): 
        The name of the sheet to read from an Excel file 
        (default: None, reads the first sheet).
    dtype (dict, optional): 
        A dictionary mapping column names to desired data types 
        (default: None, inferred from data).
    rm_newlines (bool, optional): 
        If True, removes newline characters from the data 
        (default: True).
    replace_char (str, optional): 
        The character to replace newline characters with 
        (default: empty string "").
    na_values : scalar, str, list-like, or dict, optional
        Additional strings to recognize as NA/NaN. If dict passed, specific
        per-column NA values.  By default the following values are interpreted as
        NaN: '', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan',
        '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NA', 'NULL', 'NaN', 'n/a',
        'nan', 'null'.

    Returns:
    -------
    pandas.DataFrame or pyspark.pandas.DataFrame: 
        The DataFrame containing the data from the file.

    Raises:
    -------
    ValueError: 
        If the file extension is not supported (.xlsx, .xls, or .csv).
    """
    if not na_values:
        na_values = Config.NA_VALUES

    filename = os.path.basename(file_path)
    base_name, ext = os.path.splitext(filename)
    
    file_path = db_path_to_local(file_path)

    if ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path, 
                           sheet_name=sheet_name, 
                           dtype=dtype, 
                           na_values=na_values)
    elif ext == ".csv":
        encoding=detect_file_encoding(file_path)
        df = pd.read_csv(file_path, 
                         dtype=dtype, 
                         na_values=na_values,
                         encoding=encoding)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    if rm_newlines:
        df = remove_pd_df_newlines(df, replace_char=replace_char)

    # Use str.strip() to remove leading and trailing spaces from column names
    df.columns = df.columns.str.strip()

    # Check if pyspark.pandas is available
    # if Config.USE_PYSPARK:
    #     df = ps.DataFrame(df)

    return df

# ----------------------------------------------------------------------------------

def xlsx_tabs_to_pd_dataframes(file_path, 
                               infer=True,
                               rm_newlines=True, 
                               replace_char="",
                               na_values=Config.NA_VALUES,
                               na_patterns=Config.NA_PATTERNS
                               ):
    """
    Read all sheets/tabs from an excel file into a dictionary of 
    pandas or pyspark.pandas DataFrames.

    Parameters:
    ----------
    file_path (str):
        Path to the Excel file.
    infer: (bool, optional): 
        If True, use read_df_with_optimal_dtypes to infer datatypes.
        If False, use the pandas default. 
        (default: True).
    rm_newlines (bool, optional): 
        If True, removes newline characters from the data 
        (default: True).
    replace_char (str, optional): 
        The character to replace newline characters with 
        (default: empty string "").
    na_values: (Optional) 
        List of values to consider nulls in addition to standard nulls. 
        (default: None)
    na_patterns: (Optional) 
        List of regular expressions to identify strings representing missing values. 
        (default: None)     
    Returns:
    -------
    dict
        A dictionary containing a DataFrame for each sheet in 
        the Excel file or the CSV file itself.
    """
    
    # Use a dictionary to store DataFrames
    dfs = {}

    xls = pd.ExcelFile(file_path)

    # Determine the key for the dictionary based on the file extension
    filename = os.path.basename(file_path)
    base_name, ext = os.path.splitext(filename)

    # Iterate through each worksheet and read its data into a DataFrame
    for sheet_name in xls.sheet_names:
        # Choose the appropriate function based on the 'infer' parameter
        if infer:
            df = read_df_with_optimal_dtypes(file_path, 
                                             sheet_name=sheet_name,
                                             rm_newlines=rm_newlines,
                                             replace_char=replace_char,
                                             na_values=na_values,
                                             na_patterns=na_patterns)
        else:
            df = read_spreadsheets(file_path,
                                   sheet_name=sheet_name,
                                   dtype=None, 
                                   rm_newlines=rm_newlines,
                                   replace_char=replace_char,
                                   na_values=na_values,
                                   na_patterns=na_patterns)

        # Convert to pyspark.pandas DataFrame if available
        # if Config.USE_PYSPARK:
        #     df = ps.DataFrame(df)
            

        # Set key for CSV files to ensure consistent dictionary keys
        key = base_name if ext == '.csv' else sheet_name
        dfs[key] = df

    return dfs

# ----------------------------------------------------------------------------------

def data_dict_to_json(data_dict_file, 
                      out_dir=None, 
                      out_name=None, 
                      na_values=Config.NA_VALUES, 
                      na_patterns=Config.NA_PATTERNS
                      ):
                      
    """Converts an XLSX data dictionary to a formatted JSON string.

    Reads an XLSX file containing data dictionary information, processes 
    it according to a schema, and generates a JSON representation.

    Parameters:
    ----------
    data_dict_file (str): 
        Path to the XLSX data dictionary file.
    out_dir (str, optional): 
        Path to the output directory for the JSON file. 
        Defaults to None.
    out_name (str, optional): 
        Desired name for the output JSON file (without extension). 
        Defaults to None.
    na_values: (Optional) 
        List of values to consider nulls in addition to standard nulls. 
        (default: None)
    na_patterns: (Optional) 
        List of regular expressions to identify strings representing missing values. 
        (default: None)
    Returns:
    -------
        json_string (str):
        Formatted JSON string representing the processed data dictionary.
    """
    try:
        # Read the xlxs data dictionary file, convert each tab into a dataframe, 
        # Return a dictionary {tabName: dataframe}
        dfs = xlsx_tabs_to_pd_dataframes(data_dict_file,
                                         rm_newlines=True, 
                                         replace_char='',
                                         infer=True,
                                         na_values=na_values,
                                         na_patterns=na_patterns
                                         )

        # Iterate through the dataframes to create a new subset dictionary
        data_dict = {}
        for sheet_name, df in dfs.items():
            if sheet_name.lower() == 'data_integrity':
                df = df.astype(Config.DATA_INTEGRITY_SCHEMA)
                missing_columns = set(Config.DATA_INTEGRITY_SCHEMA.keys()) - set(df.columns)
                if missing_columns:
                    raise ValueError(f"Warning: Missing columns in DATA_INTEGRITY sheet schema: {missing_columns}")
		
            # Check if each sheet/tab matches the data dictionary columns/schema and is not empty
            if set(Config.DATA_DICT_SCHEMA.keys()).issubset(set(df.columns)) and len(df) != 0:
                # Ensure data types
                if isinstance(df, ps.DataFrame):
                    df = df.to_pandas()
                df_with_types = df.astype(Config.DATA_DICT_SCHEMA, errors='ignore')
                # Ignore rows without a field/column name
                df_with_types = df_with_types.dropna(subset=[Config.DATA_DICT_PRIMARY_KEY], 
                                                     inplace=False)
                
                # Convert the dataframes into dictionaries for easier lookup
                df_with_types = df_with_types.set_index(Config.DATA_DICT_PRIMARY_KEY) 
                sheet_schema = json.loads(df_with_types.to_json(orient='index')) 
                sheet_schema = {k: {**v, Config.DATA_DICT_PRIMARY_KEY: k} 
                                for k, v in sheet_schema.items()}
                data_dict[sheet_name] = sheet_schema

        # Convert any nested string literal lists, dicts, tuples into Python objects
        data_dict = eval_nested_string_literals(data_dict)

        if out_dir and out_name:
            # Convert the dictionary to a formatted JSON string
            json_string = json.dumps(data_dict, indent=4, sort_keys=True, cls=Config.jsonEncoder)
            output_path = os.path.join(out_dir, f'{out_name}.json')
            # Save the JSON text to a file
            with open(output_path, "w") as f:
                f.write(json_string)
            print(f'Data saved to: {output_path}')

    except FileNotFoundError:
        print(f"Error: File '{data_dict_file}' not found.")
    except Exception as e:  # Catch any type of exception
        print(f"An error occurred: {e}")  # Print the error message

    return data_dict

# ----------------------------------------------------------------------------------
def read_csv_or_excel_to_df(file_path,
                            infer=True,
                            multi_sheets=True, 
                            rm_newlines=True,
                            replace_char="",
                            na_values=Config.NA_VALUES,
                            na_patterns=Config.NA_PATTERNS
                            ):
    """
    Reads a CSV or Excel file and returns data as a dictionary 
    of DataFrames, where keys are sheet names and values are 
    DataFrames containing data from each sheet.

    Parameters
    ----------
    file_path (str): 
        Path to the CSV, XLSX, or XLS file.
    infer: (bool, optional): 
        If True, use read_df_with_optimal_dtypes to infer datatypes.
        If False, use the pandas default. 
        (default: True).      
    multi_sheets : bool, optional (default=False)
        If True, allows reading multiple sheets from Excel files.
        If False, raises an error if the Excel file has multiple sheets.
    rm_newlines (bool, optional): 
        If True, removes newline characters from the data 
        (default: True).
    replace_char (str, optional): 
        The character to replace newline characters with 
        (default: empty string "").
    na_values: (Optional) 
        List of values to consider nulls in addition to standard nulls. 
        (default: None)
    na_patterns: (Optional) 
        List of regular expressions to identify strings representing missing values. 
        (default: None)
    Returns
    -------
    dict
        Returns a dictionary of DataFrames, 
        where keys are sheet names and values are DataFrames 
        containing data from each sheet.

    Raises
    ------
    ValueError
        If the file has multiple sheets and multi_sheets=False, 
        or if the file format is unsupported.
    """
        
    def read_excel_file():
        try:
            return xlsx_tabs_to_pd_dataframes(file_path, 
                                              rm_newlines=rm_newlines, 
                                              replace_char=replace_char,
                                              infer=infer,
                                              na_values=na_values,
                                              na_patterns=na_patterns)
        except ImportError:
            raise ValueError(f"Failed to import: {file_path}")

    filename = os.path.basename(file_path)
    base_name, ext = os.path.splitext(filename)

    if ext in [".xlsx", ".xls"]:
        dfs = read_excel_file()

        if not multi_sheets and len(dfs) > 1:
            sheet_names = ", ".join(dfs.keys())
            raise ValueError(f"""File contains multiple sheets: 
                {sheet_names}. Allow multi_sheets is set to False!""")
        else:
            return dfs
    elif ext == ".csv":
        if infer:
            # Read with string dtypes for accurate inference
            return {base_name: 
                    read_df_with_optimal_dtypes(file_path,
                                                rm_newlines=rm_newlines,
                                                replace_char=replace_char,
                                                na_values=na_values,
                                                na_patterns=na_patterns)}
        else:
            return {base_name: read_spreadsheets(file_path, 
                                                 sheet_name=None, 
                                                 dtype=None, 
                                                 rm_newlines=rm_newlines, 
                                                 replace_char=replace_char,
                                                 na_values=na_values,
                                                 na_patterns=na_patterns)}
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    #---------------------------------------------------------------------------------- 

def identify_leading_zeros(df_col):
    """
    Identify columns with potential leading zeros.

    Parameters:
    ----------
    df_col : pandas.Series or numpy.ndarray
        Column of a DataFrame.

    Returns:
    -------
    bool
        True if potential leading zeros are found, False otherwise.
    """
    if not isinstance(df_col, (pd.Series, np.ndarray)):
        raise ValueError("Input must be a pandas Series or numpy ndarray.")

    if isinstance(df_col, np.ndarray):
        df_col = pd.Series(df_col)

    if df_col.dtype == 'object':
        return df_col.dropna().str.startswith("0").any()
    else:
        return df_col.dropna().astype(str).str.startswith("0").any()

#---------------------------------------------------------------------------------- 

def check_all_int(df_col):
    """
    Check if all non-null values in a column can be inferred 
    as integers or floats.

    Parameters:
    ----------
    df_col : pandas.Series or numpy.ndarray
        Column of a DataFrame.

    Returns:
    -------
    type
        Data type to use for the column.
    """
    if isinstance(df_col, np.ndarray):
        df_col = pd.Series(df_col)

    _s = df_col.dropna()
    try:
        _s = pd.to_numeric(_s)
    except:
        pass

    if pd.api.types.is_bool_dtype(_s):
        return bool      
    elif pd.api.types.is_numeric_dtype(_s):
        all_ints = (_s - _s.astype(int) == 0).all()
        return 'Int64' if all_ints else 'Float64'
    else:
        return str

#---------------------------------------------------------------------------------- 

def get_non_null_values(series):
    """
    Replaces specified NA values in a pandas Series with pd.NA, drops NA values,
    and removes rows with empty strings after stripping whitespace.

    Parameters
    ----------
    series : pandas.Series
        The input pandas Series to process.

    Returns
    -------
    pandas.Series
        A Series with non-null and non-empty values.
    """

    non_null_values = series.replace(Config.NA_VALUES, pd.NA).dropna()
    non_null_values = series.replace(r'^\s+$', pd.NA, regex=True).dropna()

    return non_null_values
#---------------------------------------------------------------------------------- 

def read_spreadsheet_with_params(file_path, 
                                 sheet_name, 
                                 dtype, 
                                 na_values):
    """
    Read spreadsheet with specified parameters.

    Parameters:
    ----------
    file_path : str
        File path to the spreadsheet.
    sheet_name : str or None
        The name of the sheet to read from an Excel file.
    dtype : type or dict
        Data type or dictionary of data types to use.
    na_values : scalar, str, list-like, or dict
        Additional strings to recognize as NA/NaN.

    Returns:
    -------
    pandas.DataFrame or pyspark.pandas.DataFrame
        DataFrame containing data from the spreadsheet.
    """
    return read_spreadsheets(file_path, 
                             sheet_name=sheet_name, 
                             dtype=dtype, 
                             rm_newlines=True,
                             replace_char='',
                             na_values=na_values)

#----------------------------------------------------------------------------------

def read_df_with_optimal_dtypes(file_path,
                                sheet_name=None,
                                rm_newlines=True, 
                                replace_char='',
                                na_values=Config.NA_VALUES,
                                na_patterns=Config.NA_PATTERNS):
    """
    Infers optimal data types for a DataFrame or read, preserving 
    the best datatype for each column including leading zeros,
    boolean, strings, dates, ints, floats, etc.

    Parameters
    ----------
    file_path (str):
        File path to the CSV, XLSX, or XLS file.    
    sheet_name (str, optional): 
        The name of the sheet to read from an Excel file 
        (default: None, reads the first sheet).    
    rm_newlines (bool, optional): 
        If True, removes newline characters from the data 
        (default: True).
    replace_char (str, optional): 
        The character to replace newline characters with 
        (default: empty string "").
    na_values: (Optional) 
        List of values to consider nulls in addition to standard nulls. 
        (default: None)
    na_patterns: (Optional) 
        List of regular expressions to identify strings representing missing values. 
        (default: None)
        
    Returns
    -------
    df (pandas.DataFrame or pyspark.pandas.DataFrame): 
        A DataFrame with inferred data types.
    """
    # Initialize empty data type dictionary
    dtypes = {}

    # if Config.USE_PYSPARK:
    #     file_path = to_dbfs_path(file_path)
    # else:
    file_path = db_path_to_local(file_path)

    # Read the sheet without specifying initial data types   
    df = read_spreadsheet_with_params(file_path, sheet_name, str, na_values)
 
    # Identify any null patterns as nulls and add the observed values to the na_values
    read_as_na = na_values.copy()

    for col in df.columns:
        null_p_vals = [v for v in df[col].unique().tolist()
                       if check_na_value(v, 
                                         na_values=na_values, 
                                         na_patterns=na_patterns)
                       and not pd.isna(v)] 

        if null_p_vals:
            read_as_na.extend(list(set(null_p_vals)))

    read_as_na = list(set(read_as_na))

    # Re-read the sheet with updated na_values
    df = read_spreadsheet_with_params(file_path, 
                                      sheet_name, 
                                      str, 
                                      read_as_na)

    # Identify potential leading zeros for each column
    # is_spark_pandas = 'pyspark.pandas.frame.DataFrame' in str(type(df))
    for col in df.columns:
        non_null_values = get_non_null_values(df[col])

        
        # if is_spark_pandas:
        #     non_null_values = non_null_values.to_numpy()

        if len(non_null_values) == 0:
            dtypes[col] = object
        elif identify_leading_zeros(non_null_values):
            dtypes[col] = str  # Preserve leading zeros
        elif pd.api.types.is_bool_dtype(non_null_values):
            dtypes[col] = bool           
        elif pd.api.types.is_numeric_dtype(non_null_values):
            dtypes[col] = check_all_int(non_null_values)
        elif pd.api.types.is_string_dtype(non_null_values) or \
             pd.api.types.is_categorical_dtype(non_null_values):
            dtypes[col] = check_all_int(non_null_values)
        else:
            dtypes[col] = str             
                
    # Read the data again with the defined data types
    df = read_spreadsheet_with_params(file_path, 
                                      sheet_name, 
                                      dtypes, 
                                      read_as_na)
    
    # Attempt to convert datetime strings to datetime data types
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  
        try:
            for col in df.columns:
                df[col] = infer_datetime_column(df, col)
        except:
            pass  # leave it be

    return df

#---------------------------------------------------------------------------------- 

def infer_data_types(series):
    """
    Documents the most likely data type of a pandas or Spark Series based on 
    the non-null values in the series/column.

    Parameters
    ----------
    series (pandas.Series or pyspark.pandas.Series): 
        The series/column to analyze.

    Returns
    -------
    str: 
        The name of the data type, including the values:
        "Null-Unknown", "Boolean", "Integer", "Float", 
        "Datetime", "String", or "Other".
    """

    if 'pyspark.pandas.series.Series' in str(type(series)):
        series = series.to_pandas()

    # non_null_values = series.replace(r'^\s+$', pd.NA, regex=True).dropna()
    non_null_values = get_non_null_values(series)

    if len(non_null_values) == 0:
        return "Null-Unknown"
    else:
        if pd.api.types.is_bool_dtype(non_null_values):
            return "Boolean"
        elif pd.api.types.is_integer_dtype(non_null_values):
            return "Integer"
        elif pd.api.types.is_float_dtype(non_null_values):
            return "Float"
        elif pd.api.types.is_datetime64_any_dtype(non_null_values):
            return "Datetime"
        elif pd.api.types.is_string_dtype(non_null_values) or pd.api.types.is_categorical_dtype(non_null_values):
            try:
                converted_numeric = pd.to_numeric(non_null_values)
                if pd.api.types.is_bool_dtype(converted_numeric):
                    return "Boolean"
                if pd.api.types.is_integer_dtype(converted_numeric):
                    return "Integer"
                else:
                    return "Float"
            except:
                try:
                    dt = pd.to_datetime(non_null_values.astype(str), infer_datetime_format=True)
                    return "Datetime"
                except:
                    return "String"
        else:
            return "Other"
    

#---------------------------------------------------------------------------------- 

def check_na_value(value, 
                   na_values=Config.NA_VALUES, 
                   na_patterns=Config.NA_PATTERNS):
    """
    Checks if a value is considered a missing value based on predefined 
    patterns and custom values.

    Parameters:
    ----------
    value: 
        The value to be checked.
    na_values: (Optional) 
        List of values to consider nulls in addition to standard nulls. 
        (default: Config.NA_VALUES)
    na_patterns: (Optional) 
        List of regular expressions to identify strings representing
        missing values. 
        (default: Config.NA_PATTERNS)
    Returns:
    ----------
    bool: 
        True if the value is considered a missing/null value, 
        False otherwise.
    """
    if pd.isna(value) or value is None:
        return True    
    elif isinstance(value, str):
        if na_patterns:
            compiled_patterns = [re.compile(p) for p in na_patterns]
            if any(p.search(value) for p in compiled_patterns):
                return True
        if na_values:
            return not value.strip() or value in na_values
    else:
        return na_values and value in na_values
    return False

#---------------------------------------------------------------------------------- 

def series_hasNull(series, 
                   na_values=Config.NA_VALUES, 
                   na_patterns=Config.NA_PATTERNS):
    """
    Checks if a Pandas or Spark Pandas Series contains any null values or strings 
    matching predefined patterns.

    Parameters:
    ----------
    series : pd.Series or ps.Series
        The Series to check for null values or strings.
    na_values : list, optional
        List of values to consider as nulls 
        (default: Config.NA_VALUES).
    na_patterns : list, optional
        List of regular expressions to identify null strings 
        (default: Config.NA_PATTERNS).

    Returns:
    -------
    bool
        True if the Series contains any null values or strings 
        matching predefined patterns, 
        False otherwise.
    """
    if 'pyspark.pandas.series.Series' in str(type(series)):
        series = series.to_pandas()

    return series.apply(lambda x: check_na_value(x, na_values, na_patterns)).any()

#---------------------------------------------------------------------------------- 

def get_numeric_range(series, 
                      attribute,
                      na_val=None):
    """
    Calculates the minimum or maximum value for a numeric Series, handling both 
    numerical and non-numerical cases.

    Parameters:
        series (pd.Series or pyspark.pandas.Series): 
            The Series to process.
        attribute (str): 
            The desired statistical attribute, either 'min' or 'max'.
        na_val : (Any, optional): 
            The value to return if the Series is empty or non-numeric. 
            Defaults to 'N/A'.

    Returns:
        float, int, str: 
            The minimum or maximum value in the Series, or `na_val` if the Series is 
            empty or non-numeric. If the Series is numeric, returns the min or max 
            value as an integer if possible; otherwise, returns it as a float. If the 
            Series is empty or non-numeric, returns (na_val).
    """
    if 'pyspark.pandas.series.Series' in str(type(series)):
        series = series.to_pandas()

    _s = series.replace(r'^\s+$', pd.NA, regex=True).dropna()
    try:
        _s = pd.to_numeric(_s)
    except:
        return na_val

    if not pd.api.types.is_numeric_dtype(_s):
        return na_val

    if attribute == 'min':
        return int(_s.min()) if int(_s.min()) == float(_s.min()) else float(_s.min())
    elif attribute == 'max':
        return int(_s.max()) if int(_s.max()) == float(_s.max()) else float(_s.max())
    return na_val

#----------------------------------------------------------------------------------
def build_data_dictionary(df, 
                          max_unique_vals=100,
                          false_val='False',
                          true_val='True',
                          na_val=None
                          ):
    """
    Creates a detailed data dictionary from a Pandas or Spark DataFrame, 
    capturing key attributes for each column.

    Parameters:
    ----------
    df (pandas.DataFrame or pyspark.pandas.DataFrame): 
        The DataFrame to analyze.
    max_unique_vals (int, optional): 
        The maximum number of unique values to include in the 
        allowed value list for string columns. 
        Defaults to 100.
    false_val (str, optional): 
        The value to use for False boolean values. 
        Defaults to 'False'.
    true_val (str, optional): 
        The value to use for True boolean values. 
        Defaults to 'True'.
    na_val (str, optional): 
        The value to use for N/A or not applicable values. 
        Defaults to None.

    Returns:
    -------
    dict: A dictionary of dictionaries, each representing a column 
          with the following attributes:
        - field_name (str): Name of the column.
        - data_type (str): Data type of the column.
        - allow_null (bool): Indicates whether the column allows 
          null values.
        - null_count (int): Count of null values in the column.
        - duplicate_count (int): Count of duplicated values in 
          the column.
        - length (int or str): Maximum length of values for string 
          columns, or 'N/A' for other types.
        - range_min (float or int): Minimum value for numeric columns, 
          or 'N/A' for other types.
        - range_max (float or str): Maximum value for numeric columns, 
          or 'N/A' for other types.
        - regex_pattern (str): Regular expression pattern for the column, 
          or 'N/A' if not applicable.
        - unique_value (bool): Indicates whether the column has unique 
          values.
        - allowed_value_list (list or str): A sorted list of allowed 
          values for non-unique string columns with a manageable 
          number of unique values, or 'N/A' otherwise.
        - required (bool): Indicates whether the column is required.

    """
    is_pandas = isinstance(df, pd.DataFrame)
    is_spark_pandas = 'pyspark.pandas.frame.DataFrame' in str(type(df))

    if not (is_pandas or is_spark_pandas):
        raise ValueError("Input must be a pandas or spark.pandas DataFrame.")

    # Convert to Pandas if it's a PySpark DataFrame
    if isinstance(df, ps.DataFrame):
        df_copy = df.to_pandas()
    else:
        df_copy = df

    data_dict = {}

    for col in df_copy.columns:
        # get a null mask
        null_mask = df_copy[col].isnull()

        # Identify non-null values
        non_null_mask = ~null_mask

        # default column info structure/values (null columns)
        column_info = {
            "field_name": col,
            "data_type": "Null-Unknown",
            "allow_null": true_val,
            "null_count": int(len(df_copy)),
            "duplicate_count": 0,
            "length": na_val,
            "range_min": na_val,
            "range_max": na_val,
            "regex_pattern": na_val,  
            "unique_value": na_val,
            "allowed_value_list": na_val,
            "required": false_val
        }  

        # create column info structure/values (non-null columns)
        if not null_mask.all():
            _s = df_copy[col][non_null_mask]
            dups = _s.duplicated(keep=False)
            has_nulls = series_hasNull(df_copy[col])
            column_info = {
                "field_name": col,
                "data_type": infer_data_types(_s),
                "allow_null":  true_val if has_nulls else false_val,
                "null_count": int(null_mask.sum()),
                "duplicate_count": _s.duplicated(keep=False).sum(),
                "length": na_val,
                "range_min": get_numeric_range(_s, 'min', na_val),  
                "range_max": get_numeric_range(_s, 'max', na_val),
                "regex_pattern": na_val,
                "unique_value": true_val if dups.sum() == 0 else false_val,
                "allowed_value_list": na_val,
                "required": true_val
            }

            # document allowed values found           
            if pd.api.types.is_numeric_dtype(_s):
                try:
                    # try to cast the series as an int 
                    _s = _s.astype(int)   
                except:
                    pass 

            if pd.api.types.is_string_dtype(_s) or \
                pd.api.types.is_categorical_dtype(_s) or \
                    pd.api.types.is_integer_dtype(_s):  
                if _s.nunique() <= max_unique_vals: 
                    if pd.api.types.is_integer_dtype(_s): 
                        column_info["allowed_value_list"] = sorted([int(x) 
                                                                    for x in _s.unique()])  
                    else:
                        column_info["allowed_value_list"] = sorted(_s.astype(str).unique())  

            # document max length of values        
            if column_info["length"] == na_val:
                try:
                    # cast the series as a string 
                    _s = _s.astype(str)
                    # get the max character length in the value
                    column_info["length"] = int(_s.str.len().max())
                except:
                    pass
  
        data_dict[col] = column_info
    return data_dict

#---------------------------------------------------------------------------------- 

def dataset_schema_to_json(file_path, 
                           out_dir=None, 
                           out_name=None,
                           na_values=Config.NA_VALUES, 
                           na_patterns=Config.NA_PATTERNS
                           ):
                           
    """Generates a data dictionary JSON string given a spreadsheet
    (CSV, XLSX, or XLS) file.

    Parameters:
    ----------
    file_path (str):
        Path to the spreadsheet (CSV, XLSX, or XLS) file.
    out_dir (str, optional):
        Path to the output directory for the JSON file.
        Defaults to None.
    out_name (str, optional):
        Desired name for the output JSON file (without extension).
        Defaults to None.
    na_values: (Optional)
        List of values to consider nulls in addition to standard nulls.
        (default: None)
    na_patterns: (Optional)
        List of regular expressions to identify strings representing missing values.
        (default: None)
    Returns:
    -------
    json_string (str):
        Formatted JSON string representing the processed data dictionary.
    """

    # Initialize the schema dictionary
    schema = {}

    # Read data from CSV or Excel file
    dataframes = read_csv_or_excel_to_df(file_path, infer=True, 
                                         multi_sheets=True,
                                         na_values=na_values, 
                                         na_patterns=na_patterns)

    # Attempt to cast data types for each dataframe
    for sheet_name, dataframe in dataframes.items():
        # Generate the schema dictionary
        schema[sheet_name] = build_data_dictionary(dataframe)
        
    # Convert any nested string literal lists, dicts, tuples into Python objects
    schema = eval_nested_string_literals(schema)

    if out_dir and out_name:
        # Convert the dictionary to a JSON object
        json_string = json.dumps(schema, indent=4, sort_keys=True, cls=Config.jsonEncoder)        
        # Ensure the correct file extension
        if not out_name.endswith('.json'):
            out_name = f'{out_name}.json'
        # Ensure the correct naming convention
        if not out_name.endswith('_data_dictionary.json'):
            out_name = f'{os.path.splitext(out_name)[0]}_data_dictionary.json'
        # Build the full output path
        output_path = os.path.join(out_dir, out_name)
        # Save the JSON text to a file
        with open(output_path, "w") as file:
            file.write(json_string)
        print(f'Data dictionary saved to: {output_path}')
    
    return schema

#----------------------------------------------------------------------------------
def write_dataframes_to_xlsx(dataframes,
                             out_dir,
                             out_name,
                             sheet_order=None):
    """
    Writes a dictionary of DataFrames to an xlsx file with a given sheet
    order, handling chunking for DataFrames exceeding Excel limits.

    Parameters:
    ----------
        dataframes (dict):
            A dictionary of key-value pairs where keys are sheet
            output names and values are pandas or pyspark.pandas DataFrames.
        out_dir (str):
            Path to the output directory for the xlsx file.
        out_name (str):
            Desired name for the output xlsx file.
        sheet_order (list):
            A list specifying the desired order of the sheets in
            the output spreadsheet.
            Defaults to dictionary keys.

    Returns:
    -------
        output_path (str):
            Output path to the xlsx file
    """

    MAX_ROWS_EXCEL = 1048575  # Maximum rows allowed in an Excel sheet
    MAX_COLS_EXCEL = 16383  # Maximum columns allowed in an Excel sheet

    # If there's no ".xlsx" at all, append it
    if not out_name.endswith('.xlsx'):
        out_name = f'{out_name}.xlsx'
    output_path = os.path.join(out_dir, out_name)

    if not bool(sheet_order):
        sheet_order = list(dataframes.keys())

    # Create an ExcelWriter object
    writer = pd.ExcelWriter(output_path)

    # Create a tempfile as some environments don't allow file seek
    # (i.e dataBricks w/Azure Blob)
    temp_file = '/tmp/temp.xlsx'
    with pd.ExcelWriter(temp_file) as writer:
        # Iterate through the top-level keys (sheet names)
        for sheet_name in sheet_order:
            df = dataframes[sheet_name]

            # Convert pyspark.pandas DataFrame to pandas DataFrame if needed
            if 'pyspark.pandas.frame.DataFrame' in str(type(df)):
                df = df.to_pandas()

            # Check if splitting is needed
            if df.shape[0] > MAX_ROWS_EXCEL or df.shape[1] > MAX_COLS_EXCEL:
                chunk_size = MAX_ROWS_EXCEL
                count = 1

                for i in range(0, len(df), chunk_size):
                    chunk = df[i:i+chunk_size] 

                    # Combine the last two chunks if exceeding max rows
                    new_sheet_name = f"{count}_{sheet_name}"
                    chunk.to_excel(writer,
                                    sheet_name=new_sheet_name,
                                    index=False)
                    count += 1

            else:
                df.to_excel(writer,
                            sheet_name=sheet_name,
                            index=False)

    # Overwrite the file if it exists already
    if os.path.exists(output_path):
        os.remove(output_path)  # Remove existing file before copying
    shutil.copyfile(temp_file, output_path)
    print(f'Output saved to: {output_path}')

    try:
        os.remove(temp_file)  # Try to clean up the tempfile
    except:
        pass
    return output_path
				     
#---------------------------------------------------------------------------------- 

def dataset_schema_to_xlsx(file_path, 
                           out_dir, 
                           out_name, 
                           na_value='N/A',
                           multi_sheets=True
                           ):
                           
    """Generates a data dictionary XLSX file given a spreadsheet 
    (CSV, XLSX, or XLS) containing real data.

    Parameters:
    ----------
        file_path (str): 
            Path to the spreadsheet (CSV, XLSX, or XLS) file.
        out_dir (str, optional): 
            Path to the output directory for the JSON file. 
        out_name (str): 
            Desired name for the output JSON file (without extension). 
        na_value (str): 
            Value to use for filling missing data. 
            Defaults to 'N/A'.
        multi_sheets : bool, optional (default=True)
            If True, allows reading multiple sheets from Excel files.
            If False, raises an error if the Excel file has multiple sheets.            
    Returns:
    -------
        output_path (str):
            Output path to the XLSX file
    """

    # If there's no ".xlsx" at all, append it
    if not out_name.endswith('.xlsx'):
        out_name = f'{out_name}.xlsx'
    # If there's no "_data_dictionary" before the final ".xlsx", insert it
    if not out_name.endswith('_data_dictionary.xlsx'):
        out_name = f'{os.path.splitext(out_name)[0]}_data_dictionary.xlsx'
    output_path = os.path.join(out_dir, out_name)

    data_dictionary = {}
    dfs = read_csv_or_excel_to_df(file_path, infer=True, 
                                  multi_sheets=multi_sheets)

    for sheet_name, df in dfs.items():
        # generate the data dictionary
        data_dictionary[sheet_name] = build_data_dictionary(df)

    # Convert the data dictionary to DataFrames
    dataframes = {sheet_name: pd.DataFrame.from_dict(sheet_schema, orient='index') 
                  for sheet_name, sheet_schema in data_dictionary.items()}

    # Write the DataFrames to an XLSX file using the existing function
    write_dataframes_to_xlsx(dataframes, out_dir, out_name)

    return output_path

#----------------------------------------------------------------------------------
def get_dict_diffs(dict1, dict2):
    """
    Compares two dictionaries and returns a dictionary containing mismatches.

    Parameters:
    ----------
        dict1 (dict): 
            The test or control dictionary to compare against dict2.
        dict2 (dict): 
            The observed or actual values to compare against dict1.

    Returns:
    -------
        mismatches (dict):
            A dictionary containing differences between the two 
            dictionaries where the 'expected' key is the baseline 
            or test in dict1, and the 'observed' key is the value
            in dict2. Only unmatched values will be returned.

    Raises:
        TypeError: 
            If either `dict1` or `dict2` is not a dictionary.
    """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        raise TypeError("Both arguments must be dictionaries.")

    mismatches = {}

    for key, value in dict1.items():
        if key not in dict2:
            mismatches[key] = {"expected": value, "observed": None}
        elif isinstance(value, list) and isinstance(dict2[key], list):
            try:
                # Sort both lists for accurate comparison
                if sorted(value) != sorted(dict2[key]):
                    mismatches[key] = {"expected": value, "observed": dict2[key]}
            except TypeError:
                # If sorting fails due to type mismatch, consider it a mismatch
                mismatches[key] = {"expected": value, "observed": dict2[key]}
        else:
            try:
                # Try to cast to ints
                value = downcast_ints(value)
                dict2[key] = downcast_ints(dict2[key])

                # Attempt casting dict2[key] to the datatype of value
                if type(value)(dict2[key]) != value:
                    mismatches[key] = {"expected": value, "observed": dict2[key]}
            except (ValueError, TypeError):
                # If casting fails, consider it a mismatch
                mismatches[key] = {"expected": value, "observed": dict2[key]}

    return mismatches

#---------------------------------------------------------------------------------- 

def schema_validate_column_types(attribute, p_errors):
    """
    Checks if the observed data type matches the expected data type.

    Parameters:
    ----------
    attribute (str): 
        The name of the attribute to check.
    p_errors (dict): 
        A dictionary containing potential errors, where keys are attribute 
        names and values are dictionaries with 'expected' and 'observed' 
        values.

    Returns:
    -------
    str or None: 
        Returns the attribute name if an inequality is found, indicating 
        an error. 
        Returns None if the values match.

    Notes:
    ------
    The function uses the allowed_casting dictionary to determine if the 
    observed data type can be cast to the expected data type without loss 
    of information.
    """
    allowed_casting = {
        "String": ["String"],
        "Float": ["Float", "String"],
        "Boolean": ["Boolean", "String"],
        "Datetime": ["Datetime", "String"],
        "Integer": ["Integer", "Float", "String"],
        "Other": ["String"],
        "Null-Unknown": ["Integer", "Float", "String", "Boolean", "Datetime"]
    }

    observed_type = p_errors[attribute]['observed']
    expected_type = p_errors[attribute]['expected']

    if (expected_type != observed_type and 
        expected_type not in allowed_casting[observed_type]):
        return attribute
    return None

#---------------------------------------------------------------------------------- 

def schema_validate_column_length(attribute, p_errors):
    """
    Checks if the observed max string length of a column matches the expected 
    max string length.

    Parameters:
    ----------
    attribute (str): The name of the attribute to check.
    p_errors (dict): A dictionary containing potential errors, where keys 
                     are attribute names and values are dictionaries with 
                     'expected' and 'observed' values.

    Returns:
    -------
    str or None: Returns the attribute name if an inequality is found, 
                 indicating an error. Returns None if the values match.
    """
    obs_len = p_errors[attribute]['observed']
    exp_len = p_errors[attribute]['expected']

    is_obs_valid = isinstance(obs_len, (str, int, float))
    is_exp_valid = isinstance(exp_len, (str, int, float))

    if is_exp_valid and (not is_obs_valid or int(obs_len) > int(exp_len)):
        return attribute

    return None

#---------------------------------------------------------------------------------- 

def schema_validate_allow_null(attribute, p_errors):
    """
    Checks if null values are allowed for a given attribute.

    Parameters
    ----------
    attribute (str):
        The name of the attribute to check.
    p_errors (dict):
        A dictionary containing potential errors, where keys are attribute names
        and values are dictionaries with 'expected' and 'observed' values.

    Returns
    -------
    str or None:
        Returns the attribute name if a null value is not allowed, indicating an error.
        Returns None if null values are permitted.
    """
    if not p_errors[attribute]['expected'] and p_errors[attribute]['observed']:
        return attribute
    return None

#---------------------------------------------------------------------------------- 

def schema_validate_unique(attribute, p_errors):
    """
    Checks if column values are supposed to be unique.
    
    Parameters
    ----------
    attribute (str):
        The name of the attribute to check.
    p_errors (dict):
        A dictionary containing potential errors, where keys are attribute names
        and values are dictionaries with 'expected' and 'observed' values.

    Returns
    -------
    str or None:
        Returns the attribute name if unique values are expected but not observed, indicating an error.
        Returns None if unique values are expected and observed, or if unique values are not expected.
    """
    if p_errors[attribute]['expected'] and not p_errors[attribute]['observed']:
        return attribute
    return None

#----------------------------------------------------------------------------------
def schema_validate_range(attribute, 
                          p_errors,
                          msg_vals
                          ):
    """
    Checks if a numeric value for a given attribute falls within the expected range.

    Parameters:
    ----------
    attribute (str):
        The name of the attribute to check.
    p_errors (dict):
        A dictionary containing potential errors, where keys are attribute names
        and values are dictionaries with 'expected' and 'observed' values.
    msg_vals (dict):
        A dictionary to store values for error message formatting.

    Returns:
    -------
    str or None:
        Returns the attribute name if the value is outside the expected range,
        indicating an error. Returns None if the value is within the range.
    """

    # Check if the expected range is a numeric value
    if is_numeric_type(p_errors[attribute]['expected']):
        # Check if the observed value is also a numeric value
        if is_numeric_type(p_errors[attribute]['observed']):
            exp_val = p_errors[attribute]['expected']
            obs_val = p_errors[attribute]['observed']

            # Logic to determine when errors are flagged based on the attribute
            rng_logic = {
                'length': lambda expected, observed: expected < observed,
                'range_max': lambda expected, observed: expected < observed,
                'range_min': lambda expected, observed: expected > observed,
            }

            # Check if the observed value falls outside the expected range
            if rng_logic[attribute](exp_val, obs_val):
                # Store values for error message formatting
                msg_vals["expected"] = int(exp_val) if int(exp_val) == exp_val else exp_val
                msg_vals["observed"] = int(obs_val) if int(obs_val) == obs_val else obs_val
                return attribute
            else:
                # Update status and errors in case of data type mismatch
                p_errors[attribute]['status'] = 'Fail'
                p_errors[attribute]['errors'] = (
                    f'Data Type Error: Unable to validate {attribute}, check data types'
                )

    return None

#---------------------------------------------------------------------------------- 

def schema_validate_allowed_values(attribute, 
                                   p_errors,
                                   msg_vals
                                   ):
    """
    Checks if the observed values for a given attribute are within the allowed list.

    Parameters
    ----------
    attribute (str):
        The name of the attribute to check.
    p_errors (dict):
        A dictionary containing potential errors, where keys are attribute names
        and values are dictionaries with 'expected' and 'observed' values.
    msg_vals (dict):
        A dictionary to store values for error message formatting.

    Returns
    -------
    str or None:
        Returns the attribute name if there are values outside the allowed list,
        indicating an error. Returns None if all values are within the allowed list.
    """

    # Check if the expected and observed values are lists
    if isinstance(p_errors[attribute]['expected'], list) and isinstance(
            p_errors[attribute]['observed'], list):
        
        # Create sets for faster membership testing
        allowed_vals = set(map(str, p_errors[attribute]['expected']))
        observed_vals = set(map(str, p_errors[attribute]['observed']))

        # Check if all observed values are within the allowed list
        if not observed_vals.issubset(allowed_vals):
            # Identify values outside the allowed list
            err_vals = list(observed_vals - allowed_vals)

            # Regular expression for integers
            pattern = r"^-?\d+$"  # Matches integers only (no decimals)

            # Filter values matching the pattern
            int_vals = [int(v) for v in err_vals if re.match(pattern, str(v))]
            if len(int_vals) == len(err_vals):
                err_vals = int_vals

            # Store error values for error message formatting
            msg_vals['err_vals'] = err_vals
            return attribute

    return None

#---------------------------------------------------------------------------------- 

def schema_validate_attribute(attribute,
                              p_errors,
                              col,
                              msg_vals
                              ):
    """
    Validates specific schema attributes and returns the error type if applicable.

    Parameters:
    ----------
    attribute (str):
        The name of the attribute to validate.
    p_errors (dict):
        A dictionary containing potential errors, where keys are attribute names
        and values are dictionaries with 'expected' and 'observed' values.
    col (str):
        The name of the column being validated.
    msg_vals (dict):
        A dictionary to store values for error message formatting.

    Returns:
    -------
    str or None:
        Returns the error type if a violation is found for the attribute.
        Returns None if no errors are detected for the attribute.
    """
    # Attributes to test if expected numeric value is within a range    
    range_checks = ['length', 'range_max', 'range_min']

    if attribute == 'data_type':
        # Validate data type
        return schema_validate_column_types(attribute, p_errors)        
    elif attribute == 'allow_null':
        # Validate if null values are allowed
        return schema_validate_allow_null(attribute, p_errors)
    elif attribute == 'length':
        # Validate maximum string length
        return schema_validate_column_length(attribute, p_errors)
    elif attribute == 'unique_value':
        # Validate if column values are supposed to be unique
        return schema_validate_unique(attribute, p_errors)
    elif attribute == 'allowed_value_list':
        # Validate if observed values are within the allowed list
        return schema_validate_allowed_values(attribute, p_errors, msg_vals)        
    elif attribute in range_checks:
        # Validate if a numeric value falls within the expected range
        return schema_validate_range(attribute, p_errors, msg_vals)

    return None  # No error found for this attribute

#---------------------------------------------------------------------------------- 

def validate_schema(observed_schema,
                    data_dictionary,
                    schema_mapping
                    ):
    """
    Validates observed datasets against a data dictionary and returns 
    schema violations.

    Parameters:
    ----------
    observed_schema : dict
        The observed schema as a dictionary.
    data_dictionary : dict
        The data dictionary as a dictionary.
    schema_mapping : List[Dict]
        A list of mappings between observed datasets and corresponding 
        data dictionary sections.

    Returns:
    -------
    schema_violations : Dict
        A dictionary containing schema violations, where keys are dataset 
        names and values are dictionaries
        with flagged columns and their errors.
    """
    # Create a dict to hold schema violations
    schema_violations = {}
    _SET = Config.SCHEMA_ERROR_TEMPLATES

    # clean up the schema_mapping dict to remove references which have not data dict defined 
    # this modifies the original dictionary supplied 
    clean_mapping = schema_mapping[:]  # Create a copy
    for mapping in clean_mapping:
        data_dict_section = mapping['data_dict']
        if not data_dictionary.get(data_dict_section):
            schema_mapping.remove(mapping)
            print(f'''Warning: Authoritative schema not found for "{data_dict_section}". 
            Please check schema_mapping and update the data dictionary if needed.''')

    # Iterate over the schema_mapping object to test datasets against 
    # the given data dictionary			    
    for mapping in schema_mapping:
        observed_dataset = mapping['dataset']
        data_dict_section = mapping['data_dict']

        # Get the authoritative schema
        auth_schema = data_dictionary.get(data_dict_section)

        if not auth_schema:
            raise ValueError(f'''Authoritative schema "{data_dict_section}" not found. 
            Please check schema_mapping and update the data dictionary as needed!''')

        # Initialize the results dict
        v_results = {}

        # Iterate over columns and properties in auth_schema
        for col, col_props in auth_schema.items():
            errors = {}
            msg_vals = {"col": col,
                        'required': col_props['required']}

            # Flag potential issues initially by checking expected vs observed
            if col in observed_schema[observed_dataset].keys():
                obs_vals = observed_schema[observed_dataset][col]
                p_errors = get_dict_diffs(col_props, obs_vals)

                for atttr in p_errors:
                    error_type = None
                    msg_vals["expected"] = p_errors[atttr]['expected']
                    msg_vals["observed"] = p_errors[atttr]['observed']

                    error_type = schema_validate_attribute(atttr, 
                                                           p_errors, 
                                                           col, 
                                                           msg_vals)
                    if error_type:
                        errors[atttr] = p_errors[atttr]
                        if error_type == 'allow_null':
                            null_count = obs_vals.get('null_count')
                            if null_count:
                                msg_vals["count"] = null_count
                        if error_type == 'unique_value':
                            dup_count = obs_vals.get('duplicate_count')
                            if dup_count:
                                msg_vals["count"] = dup_count

                        errors[atttr]['errors'] = _SET[atttr].format(**msg_vals)

            elif col_props['required']:
                # Missing required column
                errors = {"required_column": {
                    "expected": True,
                    "observed": False,
                    "errors": _SET['required_column'].format(**msg_vals)}
                }
            elif not col_props['required']:
                # Missing optional column
                errors = {"optional_column": {
                    "expected": True,
                    "observed": False,
                    "errors": _SET['optional_column'].format(**msg_vals)}
                }

            if bool(errors):
                v_results[col] = {'status': 'fail', 
                                  'required': col_props['required']
                                 } | errors

        schema_violations[observed_dataset] = {'schema_violations': v_results}

    return schema_violations

#---------------------------------------------------------------------------------- 

def subset_error_df(df, column_name, unique_column=None):
    """
    Selects only the necessary columns from a DataFrame, handling different DataFrame types.

    Parameters:
    ----------
    df : pd.DataFrame or ps.DataFrame
        The DataFrame to select columns from.
    column_name : str
        The name of the column to select.
    unique_column : str, optional
        The name of the unique column to select, if it exists.

    Returns:
    -------
    pd.DataFrame:
        A regular Pandas DataFrame containing only the selected columns.
    """

    # Ensure column_name exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    columns = [column_name]
    if column_name != unique_column and (unique_column and unique_column in df.columns):
        columns.append(unique_column)
    # Convert to Pandas DataFrame if necessary
    if isinstance(df, ps.DataFrame):        
        return df[columns].to_pandas()
    else:
        return df[columns]
 
#---------------------------------------------------------------------------------- 

def value_errors_nulls(df, column_name, unique_column=None):
    """
    Identifies null values in a DataFrame column and returns their row
    indices or unique values.

    Parameters:
    ----------
    df : pd.DataFrame or pspyspark.pandas.DataFrame
        The DataFrame to check.
    column_name : str
        The name of the column to check for null values.
    unique_column : str, optional
        The name of the column containing unique values.

    Returns:
    -------
    pd.Series or pyspark.sql.pandas.Series:
        A Series containing dictionaries, each with "Sheet_Row", "Error_Type",
        'Column_Name', and the unique column value (if provided).
    """
    # Create a copy of the DataFrame with only the necessary columns
    df_copy = subset_error_df(df, 
                            column_name=column_name, 
                            unique_column=unique_column)
    
    # For Polars DataFrames, use a dictionary comprehension for efficiency
    new_columns = {
        "Error_Type": "Null Value",
        "Sheet_Row": df_copy.index + 2,  # Use original index for sheet row
        "Column_Name": column_name,
        "Lookup_Column": unique_column if unique_column in df_copy.columns else None,
        "Lookup_Value": df_copy[unique_column] if unique_column in df_copy.columns else None
    }

    return pd.DataFrame(new_columns)[df_copy[column_name].isnull()]
    
#---------------------------------------------------------------------------------- 

def value_errors_duplicates(df, column_name, unique_column=None):
    """
    Identifies duplicate values in a DataFrame column and returns their row indices,
    unique values (if provided), and the actual values from
    the column, along with error type and column name.

    Parameters:
    ----------
    df : pd.DataFrame or ps.DataFrame
        The DataFrame to check.
    column_name : str
        The name of the column to check for duplicates.
    unique_column : str, optional
        The name of the column containing unique values.

    Returns:
    -------
    pd.DataFrame or ps.DataFrame:
        A DataFrame containing the identified errors.
    """
    # Create a copy of the DataFrame with only the necessary columns
    df_copy = subset_error_df(df, 
                            column_name=column_name, 
                            unique_column=unique_column)

    # Filter for non-null values
    filtered_df = df_copy[~df_copy[column_name].isnull()]
    del(df_copy)
    # Filter for duplicates
    filtered_df = filtered_df[filtered_df[column_name].duplicated(keep=False)]

    # Create a list of dictionaries to store results (more memory-efficient)
    results = []
    for index, row in filtered_df.iterrows():
        result_dict = {
            "Error_Type": "Duplicate Value",
            "Sheet_Row": index + 2,  # Use the original index
            "Column_Name": column_name,
            "Error_Value": row[column_name],
            "Lookup_Column": unique_column if unique_column in filtered_df.columns else None,
            "Lookup_Value" : row[unique_column] if unique_column in filtered_df.columns else None
        }
        results.append(result_dict)

    # Always return a pandas DataFrame
    return pd.DataFrame(results)
    
#---------------------------------------------------------------------------------- 

def value_errors_unallowed(df, column_name, allowed_values, unique_column=None):
    """
    Identifies values in a DataFrame column that are not in a given list
    of allowed values, ensuring both the column and allowed values are strings.
    Optionally returns a unique value.

    Parameters:
    ----------
    df : pd.DataFrame or pyspark.sql.DataFrame
        The DataFrame to check.
    column_name : str
        The name of the column to check.
    allowed_values : list
        The list of allowed values.
    unique_column : str, optional
        The name of the column containing unique values.

    Returns:
    -------
    pd.DataFrame:
        A pandas DataFrame containing the identified errors.
    """

    # Ensure allowed values have the same data type as the column
    column_dtype = df[column_name].dtype
    allowed_values = pd.Series(allowed_values).astype(str)

    # Create a copy of the DataFrame with only the necessary columns
    df_copy = subset_error_df(df, 
                            column_name=column_name, 
                            unique_column=unique_column)

    # Convert the column to strings for comparison
    
    # df_copy.loc[:, column_name] = df_copy[column_name].astype(str)
    df_copy = df_copy.assign(column_name=df_copy[column_name].astype(str))

    # Create a set of allowed values for efficient lookup
    allowed_values_set = set(str(value) for value in allowed_values)

    # Filter the DataFrame based on the string comparison
    filtered_df = df_copy[~df_copy[column_name].isin(allowed_values_set)]
    del(df_copy)

    # Create a list of dictionaries to store the results
    results = []
    for index, row in filtered_df.iterrows():
        result_dict = {
            "Sheet_Row":  index + 2,  # Use the original index
            "Error_Type": 'Unallowed Value',
            'Column_Name': column_name,
            "Error_Value": row[column_name]
        }
        if unique_column:
            result_dict["Lookup_Column"] = unique_column
            result_dict["Lookup_Value" ] = row[unique_column]
        results.append(result_dict)

    # Always return a pandas DataFrame
    return pd.DataFrame(results)


#---------------------------------------------------------------------------------- 

def value_errors_length(df, column_name, max_length, unique_column=None):
    """
    Identifies values in a DataFrame column that exceed a specified maximum length,
    handling any data type by converting values to strings. Returns no results
    if all values can be converted to strings within the limit.

    Parameters:
    ----------
    df : pd.DataFrame or ps.DataFrame
        The DataFrame to check.
    column_name : str
        The name of the column to check.
    max_length : int
        The maximum allowed length for values.
    unique_column : str, optional
        The name of the column containing unique values.

    Returns:
    -------
    pd.Series or pyspark.sql.pandas.Series:
        A Series containing dictionaries, each with "Sheet_Row",
        "Error_Type", 'Column_Name', the unique column value
        (if provided), and the actual value from the 'column_name'.
        Returns an empty Series if all values can be converted to
        strings within the limit.
    """

    # Create a copy of the DataFrame with only the necessary columns
    df_copy = subset_error_df(df, 
                            column_name=column_name, 
                            unique_column=unique_column)

    try:
        str_values = df_copy[column_name].astype(str, errors='ignore').fillna('')
    except ValueError:
        return pd.Series([])

    new_columns = {
        "Error_Type": f"Value Exceeds Max Length ({max_length})",
        "Sheet_Row": df_copy.index + 2,  # Use original index for sheet row
        "Column_Name": column_name,
        "Error_Value": df_copy[column_name],
        "Lookup_Column": unique_column if unique_column in df_copy.columns else None,
        "Lookup_Value": df_copy[unique_column] if unique_column in df_copy.columns else None
    }

    return pd.DataFrame(new_columns)[str_values.str.strip().str.len() > max_length]
    
#---------------------------------------------------------------------------------- 

def value_errors_out_of_range(df, column_name, test_type, value, unique_column=None):
    """
    Identifies values in a DataFrame column that fall outside a specified range
    (either below a minimum or above a maximum value).

    Parameters:
    ----------
    df : pd.DataFrame or ps.DataFrame
        The DataFrame to check.
    column_name : str
        The name of the column to check.
    test_type : str
        'min' or 'max' indicating the type of test to perform.
    value : int or float
        The minimum or maximum allowed value, depending on the test_type.
    unique_column : str, optional
        The name of the column containing unique values.

    Returns:
    -------
    pd.DataFrame or ps.DataFrame:
        A DataFrame containing dictionaries, each with "Sheet_Row",
        "Error_Type", 'Column_Name', the unique column value
        (if provided), and the actual value from the 'column_name'.
    """

    # Create a copy of the DataFrame with only the necessary columns
    df_copy = subset_error_df(df, 
                            column_name=column_name, 
                            unique_column=unique_column)

    cleaned_column = df_copy[column_name].replace(r'^\s+$', pd.NA, regex=True)
    numeric_column = pd.to_numeric(cleaned_column, errors='coerce')

    if test_type not in ("min", "max"):
        raise ValueError("test_type must be either 'min' or 'max'")

    if pd.api.types.is_numeric_dtype(numeric_column):
        if test_type == "min":
            mask = numeric_column < value
            error_type = f"Below Minimum Allowed Value ({value})"
        elif test_type == "max":
            mask = numeric_column > value
            error_type = f"Exceeds Maximum Allowed Value ({value})"

        new_columns = {
            "Error_Type": error_type,
            "Sheet_Row": df_copy.index + 2,
            "Column_Name": column_name,
            "Error_Value": df_copy[column_name],
            "Lookup_Column": unique_column if unique_column in df_copy.columns else None,
            "Lookup_Value": df_copy[unique_column] if unique_column in df_copy.columns else None
        }

        return pd.DataFrame(new_columns)[mask]

    else:
        return pd.DataFrame([])  # No results for non-numeric columns
        
#---------------------------------------------------------------------------------- 

def value_errors_regex_mismatches(df, column_name, regex_pattern, unique_column=None):
    """
    Identifies values in a DataFrame column that do not match a
    specified regex pattern, ignoring null values.

    Parameters:
    ----------
    df : pd.DataFrame or ps.DataFrame
        The DataFrame to check.
    column_name : str
        The name of the column to check.
    regex_pattern : str
        The regular expression pattern to check against.
    unique_column : str, optional
        The name of the column containing unique values.

    Returns:
    -------
    pd.Series or ps.Series:
        A Series containing dictionaries, each with "Sheet_Row",
        "Error_Type", 'Column_Name', the unique column value
        (if provided), and the actual value from the 'column_name'.
    """

    # Create a copy of the DataFrame with only the necessary columns
    df_copy = subset_error_df(df, 
                            column_name=column_name, 
                            unique_column=unique_column)

    non_null_mask = df_copy[column_name].notnull()
    pattern_match = df_copy.loc[non_null_mask, column_name].astype(str).str.match(regex_pattern)
    mismatch_mask = ~pattern_match

    new_columns = {
        "Error_Type": "Invalid Value Formatting",
        "Sheet_Row": df_copy.index + 2,  # Use original index for sheet row
        "Column_Name": column_name,
        "Error_Value": df_copy[column_name],
        "Lookup_Column": unique_column if unique_column in df_copy.columns else None,
        "Lookup_Value": df_copy[unique_column] if unique_column in df_copy.columns else None
    }

    return pd.DataFrame(new_columns)[non_null_mask & mismatch_mask]
    
#---------------------------------------------------------------------------------- 

def get_value_errors(dataset_path, schema_errors, data_dict, 
                     schema_mapping, ignore_errors=['allow_null']):
    """
    Identifies value errors within a dataset based on the results of
    the schema validation JSON object, the data dictionary JSON object,
    and schema mapping (if required) applied against a target spreadsheet.

    Parameters:
    ----------
    dataset_path : str
        The path to the dataset file (CSV or Excel) to be validated.
    schema_errors: dict
        The result of validate_schema().
    data_dict : dict str
        The result of data_dict_to_json().
    schema_mapping : list of dicts
        A list of mappings between dataset names and corresponding
        data dictionary sections.
    ignore_errors : list, optional
        A list of error types to exclude from the analysis.
        Default is ['allow_null'].

    Returns:
    -------
    dict:
        A dictionary containing the errors for each observed dataset.
    """

    # Read the dataframes in as sheets if needed
    dfs = read_csv_or_excel_to_df(dataset_path, infer=True, multi_sheets=True)

    # Get the run UUID/file hashing
    uid = list(schema_errors.keys())[0]

    value_errors = {}
    
            
    for mapping in schema_mapping:
        observed_ds = mapping['dataset']
        data_dict_section = mapping['data_dict']
        auth_schema = data_dict.get(data_dict_section)

        if not auth_schema:
            _e = f'''Authoritative schema "{data_dict_section}" not found in keys,
            please check schema_mapping!'''
            print(_e)

            merged_errors_list = [
                            pd.DataFrame([{
                                            "Error_Type": "No Matching Schema in Data Dictionary",
                                            "Error_Value": _e,
                                            "Level": "Error",
                                        }])
                            ]
            return {uid: {observed_ds: merged_errors_list}}

        sheet_results = schema_errors[uid]["results"][observed_ds]
        sheet_v_errors = []

        df = dfs[observed_ds]
        schema_violations = sheet_results.get("schema_violations")

        unique_cols = [k for k in auth_schema.keys() if auth_schema[k]['unique_value']]
        unique_column = unique_cols[0] if unique_cols else None
        unique_column = get_best_uid_column(df, preferred_column=unique_column)

        required_cols = [k for k in auth_schema.keys() if auth_schema[k]['required']]

        if schema_violations:
            for col, errors in schema_violations.items():
                flagged_errs = list(errors.keys())
                col_required = col in required_cols 
                for error_type in ['allow_null', 'unique_value', 'length', 'range_max', 'range_min', 'allowed_value_list']:
                    if error_type in flagged_errs and error_type not in ignore_errors:
                        errs = None
                        if error_type == 'allow_null':
                            errs = value_errors_nulls(df, col, unique_column=unique_column)
                        elif error_type == 'unique_value':
                            errs = value_errors_duplicates(df, col, unique_column=unique_column)
                        elif error_type == 'length':
                            max_len = errors['length']['expected']
                            errs = value_errors_length(df, col, max_length=max_len, unique_column=unique_column)
                        elif error_type == 'range_max':
                            rng_max = errors['range_max']['expected']
                            errs = value_errors_out_of_range(df, col, test_type='max', value=rng_max, unique_column=unique_column)
                        elif error_type == 'range_min':
                            rng_min = errors['range_min']['expected']
                            errs = value_errors_out_of_range(df, col, test_type='min', value=rng_min, unique_column=unique_column)
                        elif error_type == 'allowed_value_list':
                            allowed_vals = errors['allowed_value_list']['expected']
                            errs = value_errors_unallowed(df, col, allowed_values=allowed_vals, unique_column=unique_column)
                        
                        if errs is not None and len(errs) > 0:
                            sheet_v_errors.append(
                                errs.assign(Required=col_required, 
                                            Level=Config.SCHEMA_REQUIRED_MESSAGE_LEVELS.get(col_required, "Informational/Warning")))


        if 'regex_pattern' not in ignore_errors:
            for col in df.columns:
                errs = None
                col_required =  col in required_cols 
                if auth_schema.get(col):
                    ptrn = auth_schema[col].get('regex_pattern')
                    if isinstance(ptrn, str) and ptrn not in Config.NA_VALUES:
                        errs = value_errors_regex_mismatches(df, col, regex_pattern=ptrn, unique_column=unique_column)
                        if errs is not None and len(errs) > 0: 
                            sheet_v_errors.append(
                                errs.assign(
                                    Required=col_required, 
                                    Level=Config.SCHEMA_REQUIRED_MESSAGE_LEVELS.get(col_required, "Informational/Warning")))


        merged_errors_list = []
        if bool(sheet_v_errors):
            sheet_v_errors = [df.to_pandas() if isinstance(df, ps.DataFrame) else df for df in sheet_v_errors]
            if len(sheet_v_errors) > 1:
                merged_errors_list = pd.concat(sheet_v_errors, ignore_index=True)
            elif len(sheet_v_errors) == 1:
                merged_errors_list = sheet_v_errors[0]
            else:
                merged_errors_list = []
                print('Unknown error processing value errors in : get_value_errors')
        else:
            merged_errors_list = [
                            pd.DataFrame([{
                                            "Error_Type": "None",
                                        }])
                            ]

            return {uid: {observed_ds: merged_errors_list}}

        merged_errors_list = json.loads(pd.DataFrame(merged_errors_list).to_json())
        value_errors[observed_ds] = merged_errors_list


    return {uid: value_errors}
    
#----------------------------------------------------------------------------------

def infer_and_replace_view_schema(spark, view_name):
    """
    Infers the optimal data types for columns in a Spark view and replaces the view
    with a new one using the inferred schema.

    Parameters
    ----------
    spark : SparkSession
        A SparkSession instance.
    view_name : str
        The name of the Spark view to examine and replace.

    Returns
    -------
    None
    """

    # Get the existing view as a DataFrame
    existing_view_df = spark.sql(f"SELECT * FROM {view_name}")

    # Convert the Spark DataFrame to a Pandas DataFrame
    pd_df = existing_view_df.toPandas()

    # Infer data types based on all values
    dtypes = {}
    for col in pd_df.columns:
        non_null_values = get_non_null_values(pd_df[col])
        
        if len(non_null_values) == 0:
            dtypes[col] = str  # Ensure empty columns end up as string
        elif identify_leading_zeros(non_null_values):
            dtypes[col] = str  # Preserve leading zeros
        elif pd.api.types.is_bool_dtype(non_null_values):
            dtypes[col] = bool           
        elif pd.api.types.is_numeric_dtype(non_null_values):
            dtypes[col] = check_all_int(non_null_values)
        elif pd.api.types.is_string_dtype(non_null_values) or \
             pd.api.types.is_categorical_dtype(non_null_values):
            dtypes[col] = check_all_int(non_null_values)
        else:
            dtypes[col] = str

    try:
        for col in pd_df.columns:
            pd_df[col] = infer_datetime_column(pd_df, col)
    except:
        pass  # leave it be

    # Convert the Pandas DataFrame back to a Spark DataFrame
    inferred_schema_df = ps.from_pandas(pd_df).to_spark()
    inferred_schema_df.createOrReplaceTempView(view_name)

    # Replace the view with the new DataFrame
    inferred_schema_df.createOrReplaceTempView(view_name)
    Config.SPARK_SESSION.catalog.refreshTable(view_name)

#----------------------------------------------------------------------------------

def parse_table_path(table_path):
    """
    Parse a SQL identifier into its constituent parts: host, database, schema, and table.

    Parameters
    ----------
    table_path : str
        The SQL identifier string to be parsed. It can contain up to four parts separated by dots.

    Returns
    -------
    dict
        A dictionary with keys 'host', 'database', 'schema', and 'table', where 
        each key maps to the corresponding part of the identifier. If a part is 
        not present in the identifier, its value will be None.

    """
    identifiers = table_path.split('.')
    if len(identifiers) == 0:
        return {'host': None, 'database': None, 'schema': None, 'table': table_path}
    if len(identifiers) == 4:
        return {'host': identifiers[0], 'database': identifiers[1], 'schema': identifiers[2], 'table': identifiers[3]}
    elif len(identifiers) == 3:
        return {'host': None, 'database': identifiers[0], 'schema': identifiers[1], 'table': identifiers[2]}
    elif len(identifiers) == 2:
        return {'host': None, 'database': None, 'schema': identifiers[0], 'table': identifiers[1]}
    elif len(identifiers) == 1:
        return {'host': None, 'database': None, 'schema': None, 'table': identifiers[0]}
    else:
        return {'host': None, 'database': None, 'schema': None, 'table': None}

#----------------------------------------------------------------------------------    

def load_files_to_sql(files, include_tables=[]):
    """
    Loads CSV files into Spark SQL tables if use_spark is True, otherwise into an in-memory SQLite database.

    Parameters
    ----------
    files : list of str, required
        List of paths to spreadsheet files. Default is an empty list.
    include_tables : list of str, optional
        List of table names to include. Default is an empty list.

    Returns
    -------
    tuple
        A tuple containing the connection object (None if Spark is used) and the list of table names.
    """

    table_names = []

    def is_filepath(path):
        # Regular expression to check if the path is a Databricks file path format
        file_path_pattern = re.compile(r'^(dbfs:/|/dbfs/|/mnt/|/Volumes/).+\.csv$')
        
        if file_path_pattern.match(path):
            return True
        else:
            return False
    
    if Config.USE_PYSPARK:
        print(f"Creating tables in spark with version: {Config.SPARK_SESSION.version}")
        for f in files:
            print(f'\t-Loading: {f}...')

            if not is_filepath(f):
                
                try:
                    table_path_dict = parse_table_path(f)
                    tn = table_path_dict["table"]
                    if tn:
                        table_names.append(f)
                        print(f'\t\t-Loaded: table {tn}...')
                        continue                        

                except Exception as e:
                    print(f'\t\t-Failed to load table {f}: {e}')
                    continue 


            # Get the base name of the file without extension
            base_name = os.path.splitext(os.path.basename(f))[0]
            
            # Skip the file if its base name is not in the include_tables list
            if bool(include_tables) and base_name not in include_tables:
                continue
            
            # Read the file into a dictionary of DataFrames
            dfs = read_csv_or_excel_to_df(f, infer=True)
            
            for tn, df in dfs.items():
                # Skip the table if its name is not in the include_tables list
                if bool(include_tables) and tn not in include_tables:
                    continue
                
                # Convert pandas DataFrame to pyspark.pandas DataFrame and create a Spark SQL table
                if isinstance(df, pd.DataFrame):
                    ps_df = ps.DataFrame(df)
                else:
                    ps_df = df
                ps_df.to_spark().createOrReplaceTempView(tn)
                
                infer_and_replace_view_schema(Config.SPARK_SESSION, tn)
                print(f'\t\t-Loaded: {tn}...')
                table_names.append(tn)
                # Clean up the DataFrame from memory
                # del df

        return 'pyspark_pandas', table_names

    else:
        # Create an in-memory SQLite database connection
        conn = connect(':memory:')

        for f in files:
            # Get the base name of the file without extension
            base_name = os.path.splitext(os.path.basename(f))[0]
            
            # Skip the file if its base name is not in the include_tables list
            if bool(include_tables) and base_name not in include_tables:
                continue
            
            # Read the file into a dictionary of DataFrames
            dfs = read_csv_or_excel_to_df(f)
            
            for tn, df in dfs.items():
                # Skip the table if its name is not in the include_tables list
                if bool(include_tables) and tn not in include_tables:
                    continue
                
                table_names.append(tn)
                # Create a table in the SQLite3 database for each DataFrame
                if isinstance(df, ps.DataFrame):
                    df = df.to_pandas()
                df.to_sql(tn, con=conn, if_exists="replace", index=False)
                # Clean up the DataFrame from memory
                # del df

        return conn, table_names
    
#---------------------------------------------------------------------------------- 

def extract_primary_table(sql_statement):
    """
    Extracts the full primary table path from an SQL statement using sqllineage.
    This method is generally more robust for complex SQL and qualified names.

    Parameters
    ----------
    sql_statement : str
        The SQL statement to parse.

    Returns
    -------
    str
        The full primary table path if found, otherwise None.
    """
    try:
        result = LineageRunner(sql_statement)
        tables = [
            str(tbl).replace('Table: ', '').replace('<default>.', '')
            for tbl in result.source_tables
        ]
        if tables:
            # Try to pick the first table that appears in the SQL statement
            sql_lower = sql_statement.lower()
            table_positions = [(tbl, sql_lower.find(tbl.lower())) for tbl in tables if sql_lower.find(tbl.lower()) != -1]
            if table_positions:
                # Sort by position in SQL, pick the earliest
                primary_table = sorted(table_positions, key=lambda x: x[1])[0][0]
                return primary_table
            else:
                # Fallback: return the first table from sqllineage
                return tables[0]
        return None
        return tables

    except Exception as e:
        return None

#---------------------------------------------------------------------------------- 

def extract_all_table_names(sql_statement):
    """
    Extracts all fully qualified table names from an SQL statement using sqllineage.

    Parameters
    ----------
    sql_statement : str
        The SQL statement to parse.

    Returns
    -------
    list
        A list of all fully qualified table names found in the SQL statement.
    """
    try:
        result = LineageRunner(sql_statement)
        tables = [
            str(tbl).replace('Table: ', '').replace('<default>.', '')
            for tbl in result.source_tables
        ]
        return list(set(tables))
    except Exception:
        return []

#----------------------------------------------------------------------------------

def handle_duplicate_columns(df):
    """Renames duplicate columns in a DataFrame, postfixing them with a number.

    Args:
        df (pd.DataFrame or ps.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame or ps.DataFrame: The DataFrame with unique column names.
    """
    # Create a dictionary to count occurrences of each column name
    column_count = {}
    new_columns = []

    for column in df.columns:
        if column in column_count:
            # Increment the count and create a new column name with the count
            column_count[column] += 1
            new_column_name = f"{column}_{column_count[column]}"
        else:
            # Initialize the count for the column
            column_count[column] = 0
            new_column_name = column

        new_columns.append(new_column_name)

    # Rename the columns in the DataFrame
    df.columns = new_columns

    return df

#----------------------------------------------------------------------------------

def get_rows_with_condition_spark(tables, sql_statement, error_message, error_level='error'):
    """
    Returns rows with a unique ID column value where a condition is true in the first table listed in an SQL statement.

    Parameters
    ----------
    tables : list of str
        List of table names available in Spark.
    sql_statement : str
        The SQL statement to execute.
    error_message : str
        The error message to include in the results if the condition is met.
    error_level : str, optional
        The level of the error (default is 'error').

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the primary table name, SQL error query, lookup column, and lookup value.
    """
    results = []

    # Extract the primary table name from the SQL statement
    primary_table = extract_primary_table(sql_statement)
    parser = sql_metadata.Parser(sql_statement)
    q_tbls = parser.tables
    q_tbls = [t for t in q_tbls if Config.SPARK_SESSION._jsparkSession.catalog().tableExists(t)]


    try:

        # if not all(t in tables for t in q_tbls) or primary_table not in tables:
        #     missing_tables = [t for t in q_tbls if t not in tables]
            

            # skip_msg = f"Query skipped, one or more referenced tables not found, see query for details."
            # results.append({
            # "Primary_table"     : primary_table,
            # "SQL_Error_Query"   : sql_statement,
            # "Message"           : skip_msg,
            # "Level"             : 'Skipped Query',
            # "Lookup_Column"     : '',
            # "Lookup_Value"      : ''
            # })
            # print(skip_msg)

        # else:
            
        # Get the DataFrame for the primary table
        primary_df = Config.SPARK_SESSION.table(primary_table)

        # Get the best unique ID column from the primary table
        if primary_df.count() < 10000:
            unique_column = get_best_uid_column(primary_df.toPandas())
        else:
            unique_column = get_best_uid_column(primary_df.pandas_api())

        # Register the primary table as a temporary view
        primary_df.createOrReplaceTempView("primary_table")   
                
        # Execute the modified SQL statement
        result_df = Config.SPARK_SESSION.sql(sql_statement).toPandas()

        result_df = handle_duplicate_columns(result_df)

        if len(result_df) == 0:
            # Append error information if no rows are returned
            results.append({
                "Primary_table"     : primary_table,
                "SQL_Error_Query"   : sql_statement,
                "Message"           : 'OK-No rows returned',
                "Level"             : 'Good',
                "Lookup_Column"     : '',
                "Lookup_Value"      : ''
            })
        else:
            # Prepare the results for each row in the result DataFrame
            for row_index, row in result_df.iterrows():
                results.append({
                    "Primary_table"     : primary_table,
                    "SQL_Error_Query"   : sql_statement,
                    "Message"           : error_message,
                    "Level"             : error_level,
                    "Lookup_Column"     : unique_column,
                    "Lookup_Value"      : row[unique_column]
                })
    except Exception as e:
        # Append error information if the SQL execution fails
        results.append({
            "Primary_table"     : primary_table,
            "SQL_Error_Query"   : sql_statement,
            "Message"           : f"SQL Query Failed: {str(e)}",
            "Level"             : 'SQL Error',
            "Lookup_Column"     : '',
            "Lookup_Value"      : ''
        })

    return pd.DataFrame(results)

#---------------------------------------------------------------------------------- 

def get_rows_with_condition_sqlite(tables, sql_statement, conn, error_message, error_level='error'):
    """
    Returns rows with a unique ID column value where a condition is true in the first table listed in an SQL statement.

    Parameters
    ----------
    tables : list of str
        List of table names available in the SQLite database.
    sql_statement : str
        The SQL statement to execute.
    conn : sqlite3.Connection
        The SQLite connection object.
    error_message : str
        The error message to include in the results if the condition is met.
    error_level : str, optional
        The level of the error (default is 'error').

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the primary table name, SQL error query, lookup column, and lookup value.
    """
    
    # Extract the primary table name from the SQL statement
    primary_table = extract_primary_table(sql_statement)

    # Get the best unique ID column from the primary table
    unique_column = get_best_uid_column(pd.read_sql(f'SELECT * FROM {primary_table}', conn))

    # Modify the SQL statement to select the unique ID column
    modified_sql = f"""
                    SELECT 
                        pt.{unique_column}
                    FROM ({sql_statement}) AS sq
                    LEFT JOIN {primary_table} pt ON sq.{unique_column} = pt.{unique_column}
                    """

    results = []
    try:
        # Execute the modified SQL statement
        result_df = pd.read_sql(modified_sql, conn)

        if result_df.empty:
            # Append error information if no rows are returned
            results.append({
                "Primary_table"     : primary_table,
                "SQL_Error_Query"   : sql_statement,
                "Message"           : 'OK-No rows returned',
                "Level"             : 'Good',
                "Lookup_Column"     : '',
                "Lookup_Value"      : ''
            })
        else:
            # Prepare the results for each row in the result DataFrame
            for row_index, row in result_df.iterrows():
                results.append({
                    "Primary_table"     : primary_table,
                    "SQL_Error_Query"   : sql_statement,
                    "Message"           : error_message,
                    "Level"             : error_level,
                    "Lookup_Column"     : unique_column,
                    "Lookup_Value"      : row[unique_column]
                })
    except Exception as e:
        # Append error information if the SQL execution fails
        results.append({
            "Primary_table"     : primary_table,
            "SQL_Error_Query"   : sql_statement,
            "Message"           : f"Query SQL failed: {str(e)}",
            "Level"             : 'Error',
            "Lookup_Column"     : '',
            "Lookup_Value"      : ''
        })

    return pd.DataFrame(results)

#----------------------------------------------------------------------------------

def find_errors_with_sql(data_dict_path, files, sheet_name=None):
    """
    Identifies errors in data files based on SQL rules and returns a DataFrame of errors.

    Parameters
    ----------
    data_dict_path : str
        The path to the data dictionary file (CSV or Excel) containing 
        SQL data integrity rules.
    files : list of str
        List of paths to CSV files to be loaded into an in-memory SQLite database.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the primary table name, SQL error query, lookup column, and lookup value for each error found.
    """

    # Initialize an empty DataFrame to store errors
    errors_df = pd.DataFrame()

    sql_ref_tables = []

    if not sheet_name:
        sheet_name = 'Data_Integrity'
    # Check if 'Data_Integrity' sheet exists in the Excel file
    if sheet_name in pd.ExcelFile(data_dict_path).sheet_names:
        if Config.USE_PYSPARK:
            # rules_df = ps.read_excel(to_dbfs_path(data_dict_path), sheet_name=sheet_name)  encountered bug with 'squeeze at 3.5.0
            pdf = pd.read_excel(to_dbfs_path(data_dict_path), sheet_name=sheet_name)
            rules_df = ps.from_pandas(pdf)
        else:
            rules_df = pd.read_excel(data_dict_path, sheet_name=sheet_name)

    # Extract table references from each SQL rule
    for index, row in rules_df.iterrows():
        sql_statement = row['SQL Error Query']
        sql_ref_tables.append(extract_primary_table(sql_statement))

        parser = sql_metadata.Parser(sql_statement)
        q_tbls = parser.tables
        sql_ref_tables.extend(q_tbls) 
        
    sql_ref_tables = list(set(sql_ref_tables))
    # print(f'Loading tables: {sql_ref_tables}')
    # Load CSV files into an in-memory SQLite database, including only the referenced tables
    conn, tables = load_files_to_sql(files, include_tables=sql_ref_tables)

    # Iterate over each rule in the rules DataFrame
    for index, row in rules_df.iterrows():
        sql_statement = str(row['SQL Error Query'])
        error_level = str(row['Level'])
        error_message = str(row['Message'])

        print(f'\nRunning query: \n\t\t{sql_statement}')
        if conn == 'pyspark_pandas':
            # Get rows that meet the condition specified in the SQL statement
            error_rows = get_rows_with_condition_spark(tables, sql_statement, error_message, error_level)
        else:
            # Get rows that meet the condition specified in the SQL statement
            error_rows = get_rows_with_condition_sqlite(tables, sql_statement, error_message, error_level, conn)
        
        # If there are any error rows, concatenate them to the errors DataFrame
        if not error_rows.empty:
            errors_df = pd.concat([errors_df, error_rows], ignore_index=True)
    
    return errors_df

#---------------------------------------------------------------------------------- 

def generate_integrity_summary(data_integrity_df):
    """
    Generates a summary DataFrame from the provided data 
    integrity DataFrame.

    Parameters:
    data_integrity_df (pd.DataFrame): The input DataFrame containing 
    data integrity information.

    Returns:
    pd.DataFrame: A summary DataFrame with columns 
                ['Primary_table', 'Message', 
                'Level', 'Row Quantity'].
    """
    # Define the schema for the summary DataFrame
    summ_schema = [
        'Primary_table', 'Message', 
        'Level', 'Row Quantity', 
    ]

    # Create an empty DataFrame with the defined schema
    templ_df = pd.DataFrame(columns=summ_schema).astype(str)

    # Check if the input DataFrame is not empty
    if len(data_integrity_df) > 0:

        # Group by the first four columns and count the occurrences
        summary_df = (
            data_integrity_df
            .groupby(summ_schema[0:3])
            .size()
            .reset_index(name='Row Quantity')
        )
        summary_df["Row Quantity"] = (
                                        summary_df["Row Quantity"]
                                        .where(
                                            ~(summary_df["Level"].isin(["Good", "SQL Error"]))
                                        )
                                    )

        # If the summary DataFrame is empty, use the template DataFrame
        if summary_df.empty:
            summary_df = templ_df
    else:
        # If the input DataFrame is empty, use the template DataFrame
        summary_df = templ_df

    return summary_df

#---------------------------------------------------------------------------------- 

def data_integrity(data_dict_path, csvs):
    """
    Calls find_errors_with_sql to get the data integrity DataFrame,
    then passes that DataFrame to generate_integrity_summary to get the summary.

    Parameters
    ----------
    data_dict_path : str
        The path to the data dictionary.
    csvs : list
        List of CSV file paths.

    Returns
    -------
    tuple
        A tuple containing the full results DataFrame and the summary DataFrame.
    """
    # Perform the data integrity checks
    data_integrity_df = find_errors_with_sql(data_dict_path, csvs)
    
    # Generate the summary DataFrame
    summary_df = generate_integrity_summary(data_integrity_df)
    
    return data_integrity_df, summary_df

#---------------------------------------------------------------------------------- 

def validate_dataset(dataset_path,
                     data_dict_path,
                     schema_mapping, 
                     list_errors=True,
                     out_dir=None,
                     out_name=None,
                     na_values=Config.NA_VALUES,
                     na_patterns=Config.NA_PATTERNS,
                     ignore_errors=['allow_null']
                     ): 
    """
    Validates a dataset against a data dictionary, performing both 
    schema and regex validation.
    
    Parameters
    ----------
    dataset_path : str
        The path to the dataset file (CSV or Excel) to be validated.
    data_dict_path : str
        The path to the data dictionary file (CSV or Excel) containing 
        schema and regex patterns.
    schema_mapping : list
        A list of mappings between dataset names and corresponding 
        data dictionary sections.
    list_errors : bool, optional
        Option to list all row.value level errors in a sheet/tab named
        in reference to the original dataset. 
        Defaults to True.
    out_dir : str, optional
        Path to the output directory for the JSON file. 
        Defaults to None.
    out_name : str, optional
        Desired name for the output JSON file (without extension). 
        Defaults to None.
    ignore_errors : list, optional
        A list of error types to exclude from the analysis. 
        Default is ['allow_null'].               
    Returns
    -------
    dict
        A dictionary containing the validation results.
    """
    # gather metadata 
    #----------------
    cur_ts = datetime.utcnow().isoformat()
    dataset_meta = get_spreadsheet_metadata(dataset_path) 
    data_dict_meta = get_spreadsheet_metadata(data_dict_path)

    data_dict_meta = {key: value for key, value in 
                data_dict_meta[list(data_dict_meta.keys())[0]].items() 
                if key in { "created", "file_md5_hash",
                            "file_name", "file_path",
                            "file_type", "modified"}}

    # generate the schema dictionaries to compare 
    #----------------
    data_dict = data_dict_to_json(data_dict_path, 
                                  na_values=na_values, 
                                  na_patterns=na_patterns)
    obs_schema = dataset_schema_to_json(dataset_path, 
                                        na_values=na_values, 
                                        na_patterns=na_patterns)

    # validate the observed json schema schema against the data dictionary
    #----------------
    schema_errors = validate_schema(observed_schema=obs_schema,
                                    data_dictionary=data_dict, 
                                    schema_mapping=schema_mapping)
    
    # build the output metadata 
    #---------------
    results = {}
    uid = None
    for k,v in dataset_meta.items():
        uid = f"{v['file_md5_hash']}_{data_dict_meta['file_md5_hash']}"
        results[uid] = {'run_metadata':{'start_time':cur_ts,
                                        'schema_mapping': schema_mapping},
                       'dataset_metadata':dataset_meta[k],
                       'data_dict_metadata':data_dict_meta,
                       'results': schema_errors
                      }
        
    # identify individual values errors
    #---------------
    if list_errors:
        value_errors = get_value_errors(dataset_path=dataset_path, 
                                        schema_errors=results, 
                                        data_dict=data_dict, 
                                        schema_mapping=schema_mapping,
                                        ignore_errors=ignore_errors)

        if value_errors:
            for sheet, errs in value_errors[uid].items():
                results[uid]["results"][sheet]["value_errors"]=errs

    #----------------
    # convert the dictionary to a formatted JSON string & output the results

    if bool(out_dir) and bool(out_name):
        json_string = json.dumps(results, indent=4, sort_keys=True, cls=Config.jsonEncoder)
        output_path = os.path.join(out_dir, f'{out_name}_({uid}).json')
        # save the JSON text to a file
        with open(output_path, "w") as f:
            f.write(json_string)
        print(f'Data saved to: {output_path}')
    #--------------- 
    return results

#----------------------------------------------------------------------------------

def schema_validation_to_xlsx(validation_results, 
                              out_dir, 
                              out_name=None
                              ):
    """
    Writes the dictionary results of validate_dataset to a spreadsheet
    report (.xlsx) detailing the metadata, error overview, and individual
    value errors (if included). 

    Parameters:
    ----------
        validation_results (dict):
            A dictionary of key-value pairs that are the results 
            of validate_dataset()
        out_dir (str): 
            Path to the output directory for the output xlsx file. 
        out_name (str, optional): 
            Desired name for the output xlsx file.  
            Defaults to the UUID/file hash ID string in 
            the validation_results.
    Returns:
    -------
        output_path (str):
            Output path to the xlsx file
    """
    uid = list(validation_results.keys())[0]

    # get a dataframe of metadata
    #----------------------------
    metadict = {key: value for key, value in validation_results[uid].items() 
                if key in {'run_metadata' ,'dataset_metadata', 'data_dict_metadata'}}

    metadata_df = pd.DataFrame([
                        {'Item': k, 'Attribute': k2, 'Value': v2}
                        for k, v in metadict.items() for k2, v2 in v.items()
                    ])

    rpt_sheets = {'Metadata':metadata_df}
    sheet_order = ['Metadata']

    # get a list of datasets/sheets
    datasets = list(validation_results[uid]['results'].keys())

    # get a dataframe of high level schema errors
    #----------------------------
    error_ov = []
    for ds in datasets:
        s_errs = validation_results[uid]['results'][ds].get('schema_violations')
        if not s_errs:
            continue
        for col, err_info in s_errs.items():
            if err_info['status'] == 'fail':
                req = err_info['required']

                if req is False:
                    err_info['status'] = Config.SCHEMA_REQUIRED_MESSAGE_LEVELS.get(False)

                col_errs = s_errs.get(col)
                if not bool(col_errs): 
                    continue
                for k, vals in col_errs.items():
                    if k not in ['status', 'required']:       
                        error_ov.append({
                                        'Dataset': str(ds),
                                        'Column': str(col), 
                                        'Status': str(err_info['status']).title(), 
                                        'Required': str(req).title(), 
                                        "Error_Type": str(k), 
                                        "Level": Config.SCHEMA_REQUIRED_MESSAGE_LEVELS.get(req), 
                                        'Error': str(vals['errors'])
                                        })
    if bool(error_ov):                    
        errors_ov_df = pd.DataFrame(error_ov)
    else:
        # use a blank sheet
        errors_ov_df = pd.DataFrame(columns=['Dataset', 'Column', 'Status', 
                                            'Required', "Error_Type", "Level", 'Error']) 

    rpt_sheets['Schema Overview'] = errors_ov_df
    sheet_order.append('Schema Overview')
    
    # get dataframes for each dataset/sheet of value errors
    #----------------------------
    value_errors = {}
    for ds in datasets:
        ve = validation_results[uid]['results'][ds].get('value_errors')
        if isinstance(ve, dict): 
            if 'pyspark.pandas.frame.DataFrame' in str(type(ve)):
                ve = ve.to_pandas()
            try:
                val_errs_df = pd.DataFrame(ve)
                val_errs_df = val_errs_df.sort_values(by="Sheet_Row",
                                                    ascending=True)
                value_errors[ds] = val_errs_df
            except:
                print(type(ve))
                print(ve)
                
    if bool(value_errors): 
        rpt_sheets = {**rpt_sheets, **value_errors}
        sheet_order.extend(list(value_errors.keys()))

    if not out_name:
        out_name = f"{uid}.xlsx"
    else:
        out_name = f"{out_name}_({uid}).xlsx"
    out_file = write_dataframes_to_xlsx( dataframes=rpt_sheets, 
                                            sheet_order=sheet_order, 
                                            out_dir=out_dir, 
                                            out_name=out_name)
    return(out_file)

#----------------------------------------------------------------------------------

