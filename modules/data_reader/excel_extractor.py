import polars as pl

class ExcelWorker:
    def __init__(self, parent):
        pass

    def filter_df(self, df; pl.DataFrame, filter_col: str) -> pl.DataFrame:
        """
        Filters DataFrame by a selected column
        """
        return df.filter(pl.col(filter_col).is_not_null())

    def excel_to_df(self, data: str, filter_col: str) -> dict:
        """
        Returns list of dictionaries from Excel file
        """
        df = pl.read_excel(data)
        df_filtered = self.filter_df(df, filter_col)
        return df_filtered.to_dicts()