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


def test_inventory_control_step_response_shape():
    system = linear_model.InventoryControlSystem(kp=1.5, i_target=2.0)
    t, y = system.simulate_step_response(duration=5.0, num_points=100)
    assert t.shape == y.shape
    assert len(t) == 100


def test_inventory_control_stability_positive_gain():
    system = linear_model.InventoryControlSystem(kp=0.8, i_target=1.0)
    result = system.analyze_stability()
    assert result["is_stable"] is True
