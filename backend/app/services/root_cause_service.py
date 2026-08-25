import pandas as pd

from app.ml.root_cause.analyzer import (
    RootCauseAnalyzer,
)


class RootCauseService:

    def __init__(self):

        self.analyzer = (
            RootCauseAnalyzer()
        )

    def analyze(
        self,
        dataframe: pd.DataFrame,
    ):

        return self.analyzer.analyze(
            dataframe
        )