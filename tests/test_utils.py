from trading.utils import mma

import pandas as pd
import pytest

@pytest.mark.parametrize("nb, values, mma_column", [
    (1, [0.2], [0.2]),
    (1, [0.2, 0.3, 0.4], [0.2, 0.3, 0.4]),
    (2, [0.2, 0.3, 0.4], [None, 0.25, 0.35]),
    (3, [0.2, 0.3, 0.4], [None, None, 0.3]),
])
def test_that_mma_is_computed(nb, values, mma_column):
    df = pd.DataFrame(values, columns=["high"])
    df = mma(df, nb)
    assert list(df[f"MMA{nb}"]) == mma_column
