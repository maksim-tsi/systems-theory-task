"""Nonlinear ODE models for inventory dynamics (spoilage, temperature dependence).

Implements a simple ODE integrator wrapper using scipy.integrate.odeint.
"""
from typing import Dict, Any
import numpy as np


def _decay_rate(params: Dict[str, Any]) -> float:
    decay = params.get("inventory_decay_rate", 0.01)
    temp_sens = params.get("temperature_sensitivity", 0.0)
    temperature = params.get("temperature", 20.0)
    return decay * (1 + temp_sens * (temperature - 20.0))


def inventory_ode(y, t, params: Dict[str, Any]):
    """Right-hand side of the inventory ODE.

    dy/dt = -decay_rate(T) * y + inflow(t)

    Args:
        y: Inventory scalar.
        t: Time scalar.
        params: Parameters including 'decay_rate' and 'temperature_sensitivity'.
    """
    decay_term = _decay_rate(params)
    inflow = params.get("inflow", 0.0)
    dydt = -decay_term * y + inflow
    return dydt


def inventory_replenishment_ode(state, t, params: Dict[str, Any]):
    """Two-dimensional inventory-replenishment system.

    dI/dt = R - D - decay(T) * I
    dR/dt = alpha * (I_target - I) - beta * R

    Args:
        state: [I, R]
        t: time
        params: ODE parameters

    Returns:
        Array [dI/dt, dR/dt]
    """
    inventory, repl = state
    decay = _decay_rate(params)
    demand = params.get("demand", 0.0)
    alpha = params.get("replenishment_gain", 1.0)
    beta = params.get("replenishment_decay", 1.0)
    i_target = params.get("i_target", 1.0)

    d_inventory = repl - demand - decay * inventory
    d_repl = alpha * (i_target - inventory) - beta * repl
    return np.array([d_inventory, d_repl], dtype=float)


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


def integrate_inventory_system(y0: np.ndarray, t: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
    """Integrate 2D inventory-replenishment system.

    Args:
        y0: initial state [I0, R0].
        t: times at which to evaluate solution.
        params: ODE parameters.

    Returns:
        Array of shape (len(t), 2).
    """
    try:
        from scipy.integrate import odeint
    except Exception:  # pragma: no cover - graceful fallback
        ys = np.empty((len(t), 2), dtype=float)
        ys[0] = np.asarray(y0, dtype=float)
        dt = t[1] - t[0] if len(t) > 1 else 1.0
        for i in range(1, len(t)):
            ys[i] = ys[i - 1] + dt * inventory_replenishment_ode(ys[i - 1], t[i - 1], params)
        return ys
    return odeint(lambda y, tt: inventory_replenishment_ode(y, tt, params), y0, t)


def compute_equilibrium(params: Dict[str, Any]) -> np.ndarray:
    """Compute fixed point (I*, R*) for the 2D system."""
    decay = _decay_rate(params)
    demand = params.get("demand", 0.0)
    alpha = params.get("replenishment_gain", 1.0)
    beta = params.get("replenishment_decay", 1.0)
    i_target = params.get("i_target", 1.0)

    denom = alpha / beta + decay
    if np.isclose(denom, 0.0):
        raise ValueError("Equilibrium undefined due to zero denominator.")
    inventory_star = (alpha / beta * i_target - demand) / denom
    repl_star = demand + decay * inventory_star
    return np.array([inventory_star, repl_star], dtype=float)


def jacobian_matrix(params: Dict[str, Any]) -> np.ndarray:
    """Jacobian matrix for the 2D system."""
    decay = _decay_rate(params)
    alpha = params.get("replenishment_gain", 1.0)
    beta = params.get("replenishment_decay", 1.0)
    return np.array([[-decay, 1.0], [-alpha, -beta]], dtype=float)


def classify_equilibrium(params: Dict[str, Any]) -> Dict[str, Any]:
    """Classify equilibrium by eigenvalues of the Jacobian."""
    jac = jacobian_matrix(params)
    eigvals = np.linalg.eigvals(jac)
    real = np.real(eigvals)
    imag = np.imag(eigvals)
    det = np.linalg.det(jac)

    if det < 0:
        eq_type = "saddle"
    elif np.all(np.isclose(imag, 0.0)):
        eq_type = "node"
    elif np.all(np.isclose(real, 0.0)):
        eq_type = "center"
    else:
        eq_type = "focus"

    is_stable = bool(np.all(real < 0)) if eq_type != "center" else True
    return {"type": eq_type, "eigenvalues": eigvals, "is_stable": is_stable}
