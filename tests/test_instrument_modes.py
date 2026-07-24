from liger_iris_drp_resources import gratings, make_liger_modes_table, make_iris_modes_table

def test_instrument_modes():
    modes = make_liger_modes_table()
    num_modes = 301
    assert len(modes) == num_modes, f"Expected {num_modes} modes for Liger, but got {len(modes)}."

    modes = make_iris_modes_table()
    num_modes = 310
    assert len(modes) == num_modes, f"Expected {num_modes} modes for IRIS, but got {len(modes)}."
