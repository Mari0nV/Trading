from trading.indicators.avg import (
    mma,
    mme
)

import pandas as pd
import math
import pytest

@pytest.mark.parametrize("nb, values, mma_column", [
    (1, [0.2], [0.2]),
    (1, [0.2, 0.3, 0.4], [0.2, 0.3, 0.4]),
    (2, [0.2, 0.3, 0.4], [None, 0.25, 0.35]),
    (3, [0.2, 0.3, 0.4], [None, None, 0.3]),
    (4, [0.2, 0.3, 0.4], [None, None, None]),
])
def test_that_mma_is_computed(nb, values, mma_column):
    df = pd.DataFrame(values, columns=["high"])
    df = mma(df, nb)
    assert list(df[f"MMA{nb}"]) == mma_column


@pytest.mark.parametrize("nb, alpha, values, mme_column", [
    (1, 0.5, [0.2], [0.2]),
    (1, 0.5, [0.2, 0.3, 0.4], [0.2, 0.3, 0.4]),
    (2, 0.5, [0.2, 0.3, 0.4], [None, 4/15, 11/30]),
    (3, 0.5, [0.2, 0.3, 0.4], [None, None, 12/35]),
    (3, 0.2, [0.2, 0.3, 0.4], [None, None, 96/305]),
    (3, 0, [0.2, 0.3, 0.4], [None, None, 0.3]),  # alpha = 0 -> same as MMA
    (3, 1, [0.2, 0.3, 0.4], [None, None, 0.4]),  # alpha = 1 -> only current value taken into account
    (4, 0.5, [0.2, 0.3, 0.4], [None, None, None]),
])
def test_that_mme_is_computed(nb, alpha, values, mme_column):
    df = pd.DataFrame(values, columns=["high"])
    df = mme(df, nb, alpha)
    for i in range(len(mme_column)):
        if not mme_column[i]:
            assert not df[f"MME{nb}-{alpha}"][i]
        else:
            assert math.isclose(mme_column[i], df[f"MME{nb}-{alpha}"][i])
