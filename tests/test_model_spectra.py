from liger_iris_drp_resources.model_spectra import download_model_spectra
import os

def test_model_spectra(tmp_path):
    os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] = str(tmp_path) + '/liger_iris_drp_resources'
    download_model_spectra()
    output_dir = os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] + '/Model_Spectra'
    assert os.path.exists(output_dir)
    assert any(os.listdir(output_dir)), "Downloaded model spectra directory is empty"