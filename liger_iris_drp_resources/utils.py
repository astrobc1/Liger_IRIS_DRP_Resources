import os
from astropy.utils.data import _get_download_cache_loc
import numpy as np

__all__ = [
    'get_resource_dir',
    'download',
    'to_little_endian'
]

def get_resource_dir():
    resource_dir = os.getenv('LIGER_IRIS_DRP_RESOURCE_DIR')
    if resource_dir is None:
        resource_dir = os.path.join(
            str(_get_download_cache_loc()),
            'LIGER_IRIS_DRP_RESOURCES',
        )
    return resource_dir


def download(
    model_spectra: bool = True,
    liger_psfs: bool = True,
    keck_pupil: bool = True,
    iris_psfs: bool = False,
    filter_trans: bool = True,
    micropupils: bool = True,
    skip_if_exists: bool = True
) -> str:
    """
    Download all resources from the Google Drive.

    Parameters
    ----------
    model_spectra : bool
        Whether to download the model spectra.
        Default is True.
    liger_psfs : bool
        Whether to download the Liger PSFs.
        Default is True.
    keck_pupil : bool
        Whether to download the Keck pupil image.
        Default is True.
    iris_psfs : bool
        Whether to download the IRIS PSFs.
        Default is False.
    filter_trans : bool
        Whether to download the filter transmission curves.
        Default is True.
    micropupils : bool
        Whether to download the micropupil files.
        Default is True.
    skip_if_exists : bool
        If True, skip downloading if the output directory already exists and is not empty.
        Default is True.
    """

    if model_spectra:
        from .model_spectra import download_model_spectra
        download_model_spectra(skip_if_exists=skip_if_exists)

    if liger_psfs:
        from .psfs import download_liger_psfs
        download_liger_psfs(skip_if_exists=skip_if_exists)

    if keck_pupil:
        from .psfs import download_keck_pupil_image
        download_keck_pupil_image(skip_if_exists=skip_if_exists)

    if iris_psfs:
        from .psfs import download_iris_psfs
        download_iris_psfs(skip_if_exists=skip_if_exists)

    if filter_trans:
        from .filters import download_filter_transmission_curves
        download_filter_transmission_curves(skip_if_exists=skip_if_exists)

    if micropupils:
        from .micropupils import download_micropupils
        download_micropupils(skip_if_exists=skip_if_exists)

    output_dir = get_resource_dir()
    return output_dir


def to_little_endian(arr : np.ndarray) -> np.ndarray:
    """
    Convert an array to little-endian byte order.

    Parameters
    ----------
    arr : np.ndarray
        The input array.

    Returns
    -------
    output : np.ndarray
        The input array with little-endian byte order.
    """
    if not isinstance(arr, np.ndarray):
        arr = np.asarray(arr)

    byteorder = arr.dtype.byteorder

    if byteorder == '<' or (byteorder == '=' and np.little_endian):
        return arr

    new_dtype = arr.dtype.newbyteorder('<')
    return arr.byteswap().view(new_dtype)