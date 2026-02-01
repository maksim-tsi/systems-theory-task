"""Linear (ACS) Transfer Function utilities.

Uses scipy.signal.TransferFunction when available.
"""
from typing import Tuple
import numpy as np


try:
    from scipy.signal import TransferFunction
except Exception:  # pragma: no cover - absent scipy
    TransferFunction = object


def build_acs_transfer_function(integrator_gain: float = 1.0, delay: float = 0.0):
    """Construct a simple ACS transfer function representing inventory as integrator.

    Args:
        integrator_gain: Integrator gain.
        delay: Transport delay (seconds/hours depending on units).

    Returns:
        TransferFunction-like object (scipy TransferFunction or a minimal fallback).
    """
    # Continuous-time integrator G(s) = K / s
    if TransferFunction is object:
        # Fallback: return tuple zeros/poles
        return (np.array([integrator_gain]), np.array([1.0, 0.0]))
    return TransferFunction([integrator_gain], [1.0, 0.0])
