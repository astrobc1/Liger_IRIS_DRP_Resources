from liger_iris_drp_resources import download_liger_psfs, load_liger_psf
import os

def test_liger_psfs(tmp_path):
    os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] = str(tmp_path) + '/liger_iris_drp_resources/'
    
    download_liger_psfs()

    psf_dir = os.path.join(
        os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'],
        'PSFs/Liger/PSFs_LTAO_11_09_19/ltao_7x7_YJHK/'
    )
    
    files_hy = os.listdir(os.path.join(psf_dir, 'ltao_7_7_hy'))
    assert len(files_hy) > 0, "Downloaded PSF directory is empty"

    files_kj = os.listdir(os.path.join(psf_dir, 'ltao_7_7_kj'))
    assert len(files_kj) > 0, "Downloaded PSF directory is empty"

    psf, info = load_liger_psf(mode='img', wave=1.65, xs=0, ys=0)


# def _test_iris_psfs(tmp_path):
    
#     os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'] = str(tmp_path) + '/liger_iris_drp_resources/'
    
#     download_liger_psfs()

#     psf_dir = os.path.join(
#         os.environ['LIGER_IRIS_DRP_RESOURCE_DIR'],
#         'PSFs/Liger/PSFs_LTAO_11_09_19/ltao_7x7_YJHK/'
#     )
    
#     files_hy = os.listdir(os.path.join(psf_dir, 'ltao_7_7_hy'))
#     assert len(files_hy) > 0, "Downloaded PSF directory is empty"

#     files_kj = os.listdir(os.path.join(psf_dir, 'ltao_7_7_kj'))
#     assert len(files_kj) > 0, "Downloaded PSF directory is empty"

#     psf, info = load_liger_psf(mode='img', wave=1.65, xs=0, ys=0)