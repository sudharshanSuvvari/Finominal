# service logic for each optimization strategy

import numpy as np

def equal_weights(
    holdings: list[dict[str, float]],
):

    n = len(holdings)
    
    return np.ones(n) / n