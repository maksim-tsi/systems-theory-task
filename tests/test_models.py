import numpy as np
from src import linear_model, nonlinear_model


def test_build_acs_transfer_function_returns_structure():
    tf = linear_model.build_acs_transfer_function(1.0, 0.1)
    assert tf is not None


def test_integrate_inventory_simple():
    t = np.linspace(0, 10, 11)
    ys = nonlinear_model.integrate_inventory(10.0, t, {"inventory_decay_rate": 0.1, "inflow": 0.0})
    assert ys.shape == t.shape
    assert ys[0] == 10.0
