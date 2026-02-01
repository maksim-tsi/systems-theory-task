"""Linear (ACS) Transfer Function utilities.

Uses scipy.signal.TransferFunction when available.
"""
from typing import Tuple, Dict, Any
import numpy as np


try:
    from scipy.signal import TransferFunction, pade
except Exception:  # pragma: no cover - absent scipy
    TransferFunction = object
    pade = None


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
    if delay > 0.0 and pade is not None:
        num_d, den_d = pade(delay, 1)
        num = np.polymul([integrator_gain], np.asarray(num_d, dtype=float))
        den = np.polymul([1.0, 0.0], np.asarray(den_d, dtype=float))
        return TransferFunction(num, den)
    return TransferFunction([integrator_gain], [1.0, 0.0])


def _tf_multiply(num_a: np.ndarray, den_a: np.ndarray, num_b: np.ndarray, den_b: np.ndarray):
    """Multiply two transfer functions represented as numerator/denominator arrays."""
    num = np.polymul(num_a, num_b)
    den = np.polymul(den_a, den_b)
    return num, den


def _tf_add(num_a: np.ndarray, den_a: np.ndarray, num_b: np.ndarray, den_b: np.ndarray):
    """Add two transfer functions represented as numerator/denominator arrays."""
    num = np.polyadd(np.polymul(num_a, den_b), np.polymul(num_b, den_a))
    den = np.polymul(den_a, den_b)
    return num, den


class InventoryControlSystem:
    """Feedback inventory control system with proportional controller.

    Models: I(s) = (1/s) * (U(s) - D(s)), U(t) = Kp * (I_target - I(t)).
    """

    def __init__(self, kp: float, i_target: float = 1.0, delay: float = 0.0) -> None:
        """Initialize controller gains and target.

        Args:
            kp: Proportional gain Kp.
            i_target: Target inventory level for step response.
            delay: Transport delay (lead time) in model time units.
        """
        self.kp = float(kp)
        self.i_target = float(i_target)
        self.delay = float(delay)

    def _delay_polynomials(self) -> Tuple[np.ndarray, np.ndarray]:
        if self.delay > 0.0:
            if pade is None or TransferFunction is object:
                raise RuntimeError("Delay modeling requires scipy.signal.pade.")
            num_d, den_d = pade(self.delay, 1)
            return np.asarray(num_d, dtype=float), np.asarray(den_d, dtype=float)
        return np.array([1.0]), np.array([1.0])

    def _open_loop_polynomials(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return (num_L, den_L, num_p, den_p) for open-loop and plant."""
        num_p = np.array([1.0])
        den_p = np.array([1.0, 0.0])
        num_d, den_d = self._delay_polynomials()
        num_c = np.array([self.kp])
        den_c = np.array([1.0])

        num_cd, den_cd = _tf_multiply(num_c, den_c, num_d, den_d)
        num_L, den_L = _tf_multiply(num_cd, den_cd, num_p, den_p)
        return num_L, den_L, num_p, den_p

    def _closed_loop_tf(self):
        """Build closed-loop transfer function from I_target to I."""
        if TransferFunction is object:
            raise RuntimeError("scipy.signal.TransferFunction is required for transfer functions.")
        return self.transfer_function_reference()

    def transfer_function_reference(self):
        """Closed-loop transfer function from I_target to I."""
        if TransferFunction is object:
            raise RuntimeError("scipy.signal.TransferFunction is required for transfer functions.")
        num_L, den_L, _, _ = self._open_loop_polynomials()
        den_cl = np.polyadd(den_L, num_L)
        return TransferFunction(num_L, den_cl)

    def transfer_function_disturbance(self):
        """Closed-loop transfer function from demand disturbance D to inventory I."""
        if TransferFunction is object:
            raise RuntimeError("scipy.signal.TransferFunction is required for transfer functions.")
        num_L, den_L, num_p, den_p = self._open_loop_polynomials()
        den_cl = np.polyadd(den_L, num_L)
        num_dist = -np.polymul(num_p, den_L)
        den_dist = np.polymul(den_p, den_cl)
        return TransferFunction(num_dist, den_dist)

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
