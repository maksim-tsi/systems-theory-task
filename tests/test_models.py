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


def test_inventory_equilibrium_point_matches_formula():
    params = {
        "inventory_decay_rate": 0.2,
        "temperature_sensitivity": 0.0,
        "temperature": 20.0,
        "demand": 5.0,
        "replenishment_gain": 2.0,
        "replenishment_decay": 1.0,
        "i_target": 10.0,
    }
    decay = params["inventory_decay_rate"]
    alpha = params["replenishment_gain"]
    beta = params["replenishment_decay"]
    i_target = params["i_target"]
    demand = params["demand"]
    expected_i = (alpha / beta * i_target - demand) / (alpha / beta + decay)
    expected_r = demand + decay * expected_i

    equilibrium = nonlinear_model.compute_equilibrium(params)
    assert np.allclose(equilibrium, [expected_i, expected_r])


def test_inventory_equilibrium_classification_focus():
    params = {
        "inventory_decay_rate": 0.1,
        "temperature_sensitivity": 0.0,
        "temperature": 20.0,
        "demand": 1.0,
        "replenishment_gain": 1.0,
        "replenishment_decay": 0.1,
        "i_target": 5.0,
    }
    result = nonlinear_model.classify_equilibrium(params)
    assert result["type"] == "focus"
    assert result["is_stable"] is True


def test_inventory_equilibrium_classification_node():
    params = {
        "inventory_decay_rate": 3.0,
        "temperature_sensitivity": 0.0,
        "temperature": 20.0,
        "demand": 1.0,
        "replenishment_gain": 0.1,
        "replenishment_decay": 1.0,
        "i_target": 5.0,
    }
    result = nonlinear_model.classify_equilibrium(params)
    assert result["type"] == "node"
    assert result["is_stable"] is True


def test_inventory_control_step_response_shape():
    system = linear_model.InventoryControlSystem(kp=1.5, i_target=2.0)
    t, y = system.simulate_step_response(duration=5.0, num_points=100)
    assert t.shape == y.shape
    assert len(t) == 100


def test_inventory_control_stability_positive_gain():
    system = linear_model.InventoryControlSystem(kp=0.8, i_target=1.0)
    result = system.analyze_stability()
    assert result["is_stable"] is True


def test_inventory_control_disturbance_transfer_delay_zero():
    system = linear_model.InventoryControlSystem(kp=2.0, i_target=1.0, delay=0.0)
    tf = system.transfer_function_disturbance()
    num = np.asarray(tf.num, dtype=float).ravel()
    den = np.asarray(tf.den, dtype=float).ravel()
    assert np.isclose(num[-1], -1.0)
    assert len(den) == 2
    assert np.isclose(den[-1], 2.0)


def test_inventory_control_delay_increases_order():
    system = linear_model.InventoryControlSystem(kp=1.0, i_target=1.0, delay=2.0)
    tf = system.transfer_function_reference()
    den = np.asarray(tf.den, dtype=float).ravel()
    assert len(den) > 2


def test_compute_nullclines_lines():
    params = {
        "inventory_decay_rate": 0.2,
        "temperature_sensitivity": 0.01,
        "temperature": 25.0,
        "demand": 4.0,
        "replenishment_gain": 2.0,
        "replenishment_decay": 0.5,
        "i_target": 10.0,
    }
    nullcline_i, nullcline_r = nonlinear_model.compute_nullclines(params)

    i0, i1 = 1.0, 3.0
    r0, r1 = nullcline_i(i0), nullcline_i(i1)
    decay = params["inventory_decay_rate"] * (
        1 + params["temperature_sensitivity"] * (params["temperature"] - 20.0)
    )
    expected_slope_i = decay
    observed_slope_i = (r1 - r0) / (i1 - i0)
    assert np.isclose(observed_slope_i, expected_slope_i)

    r0, r1 = nullcline_r(i0), nullcline_r(i1)
    expected_slope_r = -params["replenishment_gain"] / params["replenishment_decay"]
    observed_slope_r = (r1 - r0) / (i1 - i0)
    assert np.isclose(observed_slope_r, expected_slope_r)
