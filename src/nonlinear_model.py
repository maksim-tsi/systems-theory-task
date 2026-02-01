"""Nonlinear ODE models for inventory dynamics (spoilage, temperature dependence).

Implements a simple ODE integrator wrapper using scipy.integrate.odeint.
"""
from typing import Dict, Any
import numpy as np


def inventory_ode(y, t, params: Dict[str, Any]):
    """Right-hand side of the inventory ODE.

    dy/dt = -decay_rate(T) * y + inflow(t)

    Args:
        y: Inventory scalar.
        t: Time scalar.
        params: Parameters including 'decay_rate' and 'temperature_sensitivity'.
    """
    decay = params.get("inventory_decay_rate", 0.01)
    temp_sens = params.get("temperature_sensitivity", 0.0)
    temperature = params.get("temperature", 20.0)
    decay_term = decay * (1 + temp_sens * (temperature - 20.0))
    inflow = params.get("inflow", 0.0)
    dydt = -decay_term * y + inflow
    return dydt


def integrate_inventory(y0: float, t: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """Integrate inventory ODE over times `t`.

    Args:
        y0: initial inventory level.
        t: times at which to evaluate solution.
        params: ODE parameters.

    Returns:
        Array of y(t) values.
    """
    try:
        from scipy.integrate import odeint
    except Exception:  # pragma: no cover - graceful fallback
        # Simple Euler integrator fallback
        ys = np.empty_like(t, dtype=float)
        ys[0] = y0
        dt = t[1] - t[0] if len(t) > 1 else 1.0
        for i in range(1, len(t)):
            ys[i] = ys[i-1] + dt * inventory_ode(ys[i-1], t[i-1], params)
        return ys
    return odeint(lambda y, tt: inventory_ode(y, tt, params), y0, t).ravel()
