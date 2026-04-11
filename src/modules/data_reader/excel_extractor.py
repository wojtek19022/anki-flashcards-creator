import polars as pl

from ...constants import CONSOLE_USED

class ExcelWorker:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.logger = self.parent.logger

    def filterDf(self, df: pl.DataFrame, filter_col: str) -> pl.DataFrame:
        """
        Filters DataFrame by a selected column
        """
        return df.filter(pl.col(filter_col).is_not_null())

    def excelToDf(self, data: str, filter_col: str) -> dict:
        """
        Returns list of dictionaries from Excel file
        """
        df = pl.read_excel(data)
        df_filtered = self.filterDf(df, filter_col)
        return df_filtered.to_dicts()

    def regularExcelToDf(self, data):
        # TODO SKRYPT NIE AKCEPTUJE plikóów pyi! Trzeba to zmienić
        df = pl.read_excel(data)
        return df.to_dicts()

    def readHeaders(self, df) -> list:
        """
        Funkcja wydobywa nazwy kolumn z pierwszego arkusza excela
        """
        return df[0].keys()