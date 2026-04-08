import numpy as np

from liger_iris_drp_resources.throughput import load_throughputs


def _check_tput(waves, tput):
    assert isinstance(waves, np.ndarray)
    assert isinstance(tput, np.ndarray)
    assert len(waves) == len(tput)
    assert len(waves) > 0
    assert np.all(np.diff(waves) > 0), "Wavelengths must be strictly increasing"
    assert np.all(tput >= 0) and np.all(tput <= 1), "Throughput values must be in [0, 1]"

def test_throughput():
    params = [
        ("liger", "img", None),
        ("liger", "ifs", "slicer"),
        ("liger", "ifs", "lenslet"),
        ("iris", "img", None),
        ("iris", "ifs", None),
    ]
    for p in params:
        print(f"Testing load_throughputs with parameters: {p}")
        waves, tput = load_throughputs(*p)
        _check_tput(waves, tput)
