import polars as pl

from ...constants import CONSOLE_USED

class ExcelWorker:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.logger = self.parent.logger

    def filter_df(self, df: pl.DataFrame, filter_col: str) -> pl.DataFrame:
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

    def regular_excel_to_df(self, data):
        # TODO SKRYPT NIE AKCEPTUJE plikóów pyi! Trzeba to zmienić
        df = pl.read_excel(data)
        return df.to_dicts()

    def read_headers(self, df):
        """
        Funkcja wydobywa nazwy kolumn z pierwszego arkusza excela
        """
        return df[0].keys()