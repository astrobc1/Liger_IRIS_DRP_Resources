import os
import numpy as np
from liger_iris_drp_resources.micropupils import download_micropupils, load_micropupil_for_filter


def test_get_micropupils(tmp_path):

    os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] = str(tmp_path) + '/liger_iris_drp_resources'

    download_micropupils()

    mp_dir = os.path.join(
        os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'],
        'micropupils'
    )

    assert any(os.listdir(mp_dir)), "Downloaded micropupils directory is empty"

    mp, mp_file = load_micropupil_for_filter(filter_name='KN2')

    assert isinstance(mp, np.ndarray), "Micropupil is not a numpy array"
    assert mp.shape == (61, 61)
    assert os.path.basename(mp_file) == 'mp2.0700.fits'