import os
import numpy as np
from liger_iris_drp_resources.filters import load_filters_summary
from liger_iris_drp_resources.filters import download_filter_transmission_curves, load_filter_transmission_curve

def test_filters_summary():
    
    fd = load_filters_summary()

    assert isinstance(fd, dict)
    assert len(fd) > 0

    for name, info in fd.items():
        assert info['wavemin'] > 0
        assert info['wavemax'] > info['wavemin'], f"wavemax <= wavemin for {name}"
        assert info['wavecenter'] > info['wavemin'], f"wavecenter <= wavemin for {name}"
        assert info['wavecenter'] < info['wavemax'], f"wavecenter >= wavemax for {name}"


def test_filters_curves(tmp_path):

    os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] = str(tmp_path) + '/liger_iris_drp_resources'

    download_filter_transmission_curves()

    trans_dir = os.path.join(
        os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'],
        'Filters'
    )

    assert any(os.listdir(trans_dir)), "Downloaded filter transmission curves directory is empty"

    wave, trans = load_filter_transmission_curve(filter_name='Y')

    assert isinstance(wave, np.ndarray)
    assert isinstance(trans, np.ndarray)
    assert len(wave) > 0
    assert len(trans) > 0