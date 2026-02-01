"""Linear (ACS) Transfer Function utilities.

Uses scipy.signal.TransferFunction when available.
"""
from typing import Tuple, Dict, Any
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


class InventoryControlSystem:
    """Feedback inventory control system with proportional controller.

    Models: I(s) = (1/s) * (U(s) - D(s)), U(t) = Kp * (I_target - I(t)).
    """

    def __init__(self, kp: float, i_target: float = 1.0) -> None:
        """Initialize controller gains and target.

        Args:
            kp: Proportional gain Kp.
            i_target: Target inventory level for step response.
        """
        self.kp = float(kp)
        self.i_target = float(i_target)

    def _closed_loop_tf(self):
        """Build closed-loop transfer function from I_target to I."""
        if TransferFunction is object:
            raise RuntimeError("scipy.signal.TransferFunction is required for transfer functions.")
        # Closed-loop: Kp/(s + Kp)
        return TransferFunction([self.kp], [1.0, self.kp])

    def simulate_step_response(
        self,
        duration: float = 10.0,
        num_points: int = 500,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate step response of inventory to I_target step input.

        Args:
            duration: Simulation horizon.
            num_points: Number of time points.

        Returns:
            (t, y) arrays for time and inventory response.
        """
        t = np.linspace(0.0, duration, num_points)
        try:
            from scipy.signal import step

            tf = self._closed_loop_tf()
            t_out, y = step(tf, T=t)
            return t_out, y * self.i_target
        except Exception:  # pragma: no cover - fallback without scipy
            y = self.i_target * (1.0 - np.exp(-self.kp * t))
            return t, y

    def analyze_stability(self) -> Dict[str, Any]:
        """Check closed-loop stability via pole locations.

        Returns:
            Dict with poles and stability flag.
        """
        tf = self._closed_loop_tf()
        den = np.asarray(tf.den, dtype=float).ravel()
        poles = np.roots(den)
        is_stable = np.all(np.real(poles) < 0)
        return {"poles": poles, "is_stable": bool(is_stable)}
