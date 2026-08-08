import importlib.resources
import astropy.io.fits as fits
import numpy as np
import os

from .utils import get_resource_dir

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'load_ifs_array_mask',
    'load_ifs_trace_geometry',
]

def load_ifs_array_mask() -> str:
    """
    Retrieve the IFS array mask.

    Returns
    -------
    arr_mask : np.ndarray
        The lenslet array mask.
    filepath : str
        The path to the lenslet array mask file that was loaded.
    """
    filename = 'arr_mask.npy'
    filepath = importlib.resources.files('liger_iris_drp_resources') / f'resources/trace_geometry/{filename}'
    arr_mask = np.load(filepath)
    arr_mask = arr_mask.astype(np.int64)
    return arr_mask


def _get_ifs_trace_geometry_filepath(ifs_mode: str, filter_name: str, resolution: int) -> str:
    """
    Get the filename for the lenslet trace geometry data based on filter name and resolution.

    Parameters
    ----------
    ifs_mode : str
        The IFS mode (lenslet or slicer).
    filter_name : str
        The name of the filter.
    resolution : int
        The spectral resolution.

    Returns
    -------
    filename : str
        The filename for the lenslet trace geometry data.
    """
    filename = f"{filter_name}_{int(resolution)}.csv"
    filepath = importlib.resources.files('liger_iris_drp_resources') / f'resources/trace_geometry/{ifs_mode.lower()}/{filename}'
    return str(filepath)


def load_ifs_trace_geometry(
    ifs_mode : str,
    filter_name : str,
    resolution : int,
    shape : tuple[int, int] = (4096, 4096),
    pixel_size_um : float = 15.0
) -> tuple[np.ndarray, str]:
    """
    Load the lenslet trace geometry for a given filter and resolution.

    Parameters
    ----------
    ifs_mode : str
        The IFS mode (lenslet or slicer).
    filter_name : str
        The name of the filter.
    resolution : int
        The spectral resolution.
    shape : tuple[int, int], optional
        The shape of the detector, by default (4096, 4096).
    pixel_size_um : float, optional
        The size of each pixel in micrometers, by default 15.0.
    
    Returns
    -------
    trace_geometry : np.ndarray
        The IFS trace geometry data.
    filepath : str
        The path to the IFS trace geometry file that was loaded.
    """

    # Load the lenslet trace geometry data
    filepath = _get_ifs_trace_geometry_filepath(ifs_mode, filter_name, resolution)
    data = np.loadtxt(filepath, delimiter=" ")
    file_x_mm = data[:, [4, 6, 8, 10, 12]]
    file_y_mm = data[:, [5, 7, 9, 11, 13]]

    # file y is the dispersion axis
    x_mm, y_mm = file_y_mm, file_x_mm

    # Convert to pixel coordinates
    x_pix = x_mm * 1000.0 / pixel_size_um + shape[1] / 2.0 - 0.5
    y_pix = y_mm * 1000.0 / pixel_size_um + shape[0] / 2.0 - 0.5

    # Convert to float32
    x_pix = x_pix.astype(np.float32)
    y_pix = y_pix.astype(np.float32)

    return x_pix, y_pix


def _get_trace_geometry_dir() -> str:
    return os.path.join(get_resource_dir(), 'trace_geometry')