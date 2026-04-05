import os
import re
import zipfile
import gdown
import numpy as np
from astropy.io import fits
from astropy.utils.data import _get_download_cache_loc
import astropy.time

from .utils import get_resource_dir

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'load_liger_psf',
    'load_iris_psf',
    'download_liger_psfs',
]

####################
#### Liger PSFs ####
####################

def _get_liger_psf_dir() -> str:
    return os.path.join(get_resource_dir(), 'PSFs/Liger')

def download_liger_psfs(output_dir: str | None = None) -> str:
    """
    Download the LIGER PSFs from the Google Drive.

    Parameters
    ----------
    output_dir : str | None
        The directory to save the PSF folder to.

    Returns
    -------
    str
        The directory containing the downloaded PSF files.
    """
    if output_dir is None:
        output_dir = _get_liger_psf_dir()

    os.makedirs(output_dir, exist_ok=True)

    url = 'https://drive.google.com/drive/folders/1aWN7B4IMsG2c6lV9WVNY3qWsq5C_YIKi?usp=drive_link'
    timestamp = astropy.time.Time.now().iso.replace(":", "-").replace(".", "-")
    temp_zip = os.path.join(output_dir, f"liger_psfs_{timestamp}.zip")

    logger.info(f"Downloading Liger PSFs to {output_dir}...")

    gdown.download(url=url, output=temp_zip, quiet=False, fuzzy=True)

    if not os.path.exists(temp_zip):
        msg = f"Failed to download PSFs: file not found at {temp_zip}"
        logger.error(msg)
        raise RuntimeError(msg)

    try:
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            extracted_files = zip_ref.namelist()

            if not extracted_files:
                msg = "Downloaded PSF zip archive is empty"
                logger.error(msg)
                raise RuntimeError(msg)

            zip_ref.extractall(output_dir)

        logger.info(f"Successfully downloaded and extracted Liger PSFs to {output_dir}")
        return output_dir

    except zipfile.BadZipFile as e:
        logger.error(f"Downloaded file {temp_zip} is not a valid zip archive: {e}")
        raise RuntimeError("Invalid zip archive for Liger PSFs") from e
    finally:
        if os.path.exists(temp_zip):
            os.remove(temp_zip)


def load_liger_psf(
    wave : float, xs : float, ys : float,
    psf_dir : str | None = None
) -> tuple[np.ndarray, dict]:
    """
    Load a LIGER PSF for a given wavelength and position.

    Parameters
    ----------
    wave : float
        The wavelength in nanometers.
    xs : float
        The x position in arcseconds.
    ys : float
        The y position in arcseconds.
    psfdir : str | None
        The directory containing the PSF files.
        Defaults to the LIGER_IRIS_DRP_DATA_DIR environment variable.

    Returns
    -------
    tuple[np.ndarray, dict]
        The PSF image and its metadata.
    """

    # Determine "closest" PSFs in wavelength and position
    xs_ao = np.array([-15, -10, -5, 0, 5, 10, 15])
    ys_ao = np.array([-15, -10, -5, 0, 5, 10, 15])
    xs = xs_ao[np.argmin(np.abs(xs_ao - xs))]
    ys = xs_ao[np.argmin(np.abs(ys_ao - ys))]
    liger_psf_filters = ['Y', 'J', 'H', 'K']
    liger_psf_filter_waves = np.array([1020, 1248, 1650, 2124])
    filt = liger_psf_filters[np.argmin(np.abs(liger_psf_filter_waves - wave))]

    # Get psf directory
    if psf_dir is None:
        psf_dir = get_liger_psf_dir()

    # Select file from filter and position
    if filt == 'Y':
        filename = os.path.join(
            psf_dir,
            'LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_hy',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 1
    elif filt == 'J':
        filename = os.path.join(
            psf_dir,
            'LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_jk',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 1
    elif filt == 'H':
        filename = os.path.join(
            psf_dir,
            'LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_hy',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 0
    elif filt == 'K':
        filename = os.path.join(
            psf_dir,
            'LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_hy',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 0
    psf, info = _read_liger_psf_file(filename, hdunum)
    return psf, info


def _parse_liger_psf_loc(filename : str) -> tuple[int, int]:
    match = re.search(r"_x([-+]?\d+)_y([-+]?\d+)", os.path.basename(filename))
    x, y = match.group(1), match.group(2)
    x, y = int(x), int(y)
    return x, y


def _read_liger_psf_file(
    filename : str, hdunum : int | None = None,
) -> tuple[np.ndarray, dict]:
    with fits.open(filename) as hdulist:
        psf = hdulist[hdunum].data
        info = _parse_liger_psf_header(hdulist[hdunum].header)
        info['filename'] = filename
        info['hdunum'] = hdunum
        info['position'] = _parse_liger_psf_loc(filename)
    # Ensure odd shape
    # NOTE: This needs futher explanation why the PSFs have an even shape
    # NOTE: We may need to interpolate instead, TBD
    if psf.shape[0] % 2 == 0:
        psf = psf[1:, :].copy()
    if psf.shape[1] % 2 == 0:
        psf = psf[:, 1:].copy()
    return psf, info


def _parse_liger_psf_header(header : fits.Header):
    info = {}
    info['r0'] = header['R0'] * 1E6 # meters -> microns
    info['l0'] = header['L0'] * 1E6 # meters -> microns
    info['wavelength'] = header['WVL'] * 1E6 # meters -> microns
    info['opd_sampling'] = header['DT'] * 1E6 # meters -> microns
    info['fft_grid'] = int(header['NFFT'].real)
    info['psf_sampling'] = header['DP']
    info['sum'] = header['SUM']
    info['itime'] = header['DT']
    info['theta'] = float(header['THETA'].real)
    return info


###################
#### IRIS PSFs ####
###################

