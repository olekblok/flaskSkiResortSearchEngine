import pandas as pd


class DataProcessor:
    @staticmethod
    def clean_km_total(value: str) -> float:
        if value == 'Additional':
            return 0
        value = value.replace('km', '').replace('Total:', '').strip()
        return float(value)

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        columns_to_clean = ['total_slopes', 'blue_slopes', 'red_slopes', 'black_slopes', 'total_lifts']

        df[columns_to_clean] = df[columns_to_clean].applymap(self.clean_km_total)

        return df


