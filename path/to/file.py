    converted_series = non_null_values.apply(try_dateutil_parser)
    successfully_converted_count = converted_series.dropna().count()

    # Guard: if parsing failed completely, skip this column
    if successfully_converted_count == 0:
        return df[column_name] if is_spark_pandas else orig_series

    combined_series = pd.Series(index=series_for_processing.index, dtype='datetime64[ns]')
    combined_series.loc[converted_series.index] = converted_series
    successfully_converted_count = combined_series.dropna().count()
    if successfully_converted_count / non_null_count >= 0.98:
        return ps.Series(combined_series) if is_spark_pandas else combined_series
