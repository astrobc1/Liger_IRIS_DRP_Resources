import os
import re
import zipfile
import gdown
import numpy as np
from astropy.io import fits

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
    url = 'https://drive.google.com/file/d/1ZW1ePWObhQTJnwZK02EuPwJOxjCf4xbg/view?usp=drive_link'
    logger.info(f"Downloading Liger PSFs to {output_dir}...")
    temp_zip = gdown.download(url=url, output=os.path.join(output_dir, 'liger_psfs.zip'), quiet=False, fuzzy=True)
    if temp_zip is None or not os.path.exists(temp_zip):
        msg = "Failed to download PSFs"
        logger.error(msg)
        raise RuntimeError(msg)
    try:
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            extracted_files = zip_ref.namelist()
            if not extracted_files:
                msg = "Downloaded PSF zip archive is empty"
                logger.error(msg)
                raise RuntimeError(msg)
            top_level_names = {
                f.split('/')[0] for f in extracted_files
                if 'MACOSX' not in f and not f.startswith('.')
            }
            if not top_level_names:
                msg = "No valid top-level folder found in PSF zip archive"
                logger.error(msg)
                raise RuntimeError(msg)
            if len(top_level_names) > 1:
                logger.warning(f"Multiple top-level entries found in zip: {top_level_names}. Using first sorted entry.")
            top_level_folder = sorted(top_level_names)[0]
            zip_ref.extractall(output_dir)
        final_dir = os.path.join(output_dir, top_level_folder)
        logger.info(f"Successfully downloaded and extracted Liger PSFs to {final_dir}")
        return final_dir
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
    ys = ys_ao[np.argmin(np.abs(ys_ao - ys))]

    liger_psf_filters = ['Y', 'J', 'H', 'K']
    liger_psf_filter_waves = np.array([1020, 1248, 1650, 2124])
    filt = liger_psf_filters[np.argmin(np.abs(liger_psf_filter_waves - wave))]

    # Get psf directory
    if psf_dir is None:
        psf_dir = _get_liger_psf_dir()

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

