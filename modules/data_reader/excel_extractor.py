import polars as pl

class ExcelWorker:
    def __init__(self):
        pass

    @staticmethod
    def excel_to_df(data: str) -> dict:
        return pl.read_excel(data).to_dicts()