import os
import numpy as np
from liger_iris_drp_resources.trace_geometry import load_ifs_array_mask, load_ifs_trace_geometry

def test_arr_mask(tmp_path):
    
    os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] = str(tmp_path) + '/liger_iris_drp_resources'
    
    arr_mask = load_ifs_array_mask()

    assert isinstance(arr_mask, np.ndarray)
    assert arr_mask.shape == (128, 128)


def test_ifs_trace_geometry(tmp_path):

    os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] = str(tmp_path) + '/liger_iris_drp_resources'

    x_pix, y_pix = load_ifs_trace_geometry(
        ifs_mode='lenslet',
        filter_name='KN2',
        resolution=4000,
    )

    assert isinstance(x_pix, np.ndarray)
    assert isinstance(y_pix, np.ndarray)
    assert x_pix.shape[0] == 128 * 128
    assert x_pix.shape[1] == 5
    assert y_pix.shape[0] == 128 * 128
    assert y_pix.shape[1] == 5