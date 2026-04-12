import os
import re
import zipfile
import gdown
import numpy as np
from astropy.io import fits

from .utils import get_resource_dir, to_little_endian

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'get_liger_psf',
    'get_iris_psf',
    'download_liger_psfs',
    'download_iris_psfs',
]

####################
#### Liger PSFs ####
####################

def _get_liger_psf_dir() -> str:
    return os.path.join(get_resource_dir(), 'PSFs/Liger')

def download_liger_psfs(
    output_dir: str | None = None,
    skip_if_exists: bool = True
) -> str:
    """
    Download the LIGER PSFs from the Google Drive.
    
    Parameters
    ----------
    output_dir : str | None
        The directory to save the PSF folder to.
    skip_if_exists : bool
        If True, skip downloading if the output directory already exists and is not empty.
        Default is True.
    
    Returns
    -------
    str
        The directory containing the downloaded PSF files.
    """
    if output_dir is None:
        output_dir = _get_liger_psf_dir()

    if skip_if_exists and os.path.exists(output_dir) and any(os.listdir(output_dir)):
        logger.info(f"PSF directory {output_dir} already exists and is not empty. Skipping download.")
        return output_dir
    
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

def _get_liger_psf_filename(
    wave : float, xs : float, ys : float,
) -> tuple[str, int]:
    
    # Determine "closest" PSFs in wavelength and position
    xs_ao = np.array([-15, -10, -5, 0, 5, 10, 15])
    ys_ao = np.array([-15, -10, -5, 0, 5, 10, 15])

    xs = xs_ao[np.argmin(np.abs(xs_ao - xs))]
    ys = ys_ao[np.argmin(np.abs(ys_ao - ys))]

    liger_psf_bps = ['Y', 'J', 'H', 'K']
    liger_psf_filter_waves = np.array([1.02, 1.248, 1.65, 2.124])
    bp = liger_psf_bps[np.argmin(np.abs(liger_psf_filter_waves - wave))]
    if bp == 'Y':
        filename = os.path.join(
            'PSFs_LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_hy',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 1
    elif bp == 'J':
        filename = os.path.join(
            'PSFs_LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_kj',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 1
    elif bp == 'H':
        filename = os.path.join(
            'PSFs_LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_hy',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 0
    elif bp == 'K':
        filename = os.path.join(
            'PSFs_LTAO_11_09_19',
            'ltao_7x7_YJHK',
            'ltao_7_7_hy',
            f"evlpsfcl_1_x{xs}_y{ys}.fits",
        )
        hdunum = 0

    return filename, hdunum

def get_liger_psf(
    wave : float, xs : float, ys : float,
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

    Returns
    -------
    tuple[np.ndarray, dict]
        The PSF image and its metadata.
    """

    # Get psf filepath and HDU
    psf_dir = _get_liger_psf_dir()
    filename, hdunum = _get_liger_psf_filename(wave, xs, ys)
    filepath = os.path.join(psf_dir, filename)

    # Load PSF
    psf, info = _read_liger_psf_file(filepath, hdunum)

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
    psf = to_little_endian(psf)
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

def _get_iris_psf_dir() -> str:
    return os.path.join(get_resource_dir(), 'PSFs/IRIS')

def download_iris_psfs(
    output_dir: str | None = None,
    skip_if_exists: bool = True
) -> str:
    raise NotImplementedError("IRIS PSF download not implemented yet")



def get_iris_psf(
    mode : str,
    wave : float,
    xs : float = 0, ys : float = 0,
    itime : float = 300,
    zenith : str = '45',
    atm : str = '50',
):
    """
    Get the IRIS PSF for the imager or IFS for the given input parameters.

    Parameters
    ----------
    mode : str
        The mode ('img', 'ifs').
    wave : float
        The wavelength in microns.
    xs : float
        The x offset in arcsec from on-axis. Default is 0.
    ys : float
        The y offset in arcsec from on-axis. Default is 0.
    itime : float
        The integration time in seconds. Default is 300.
    zenith : str
        The zenith angle in degrees. Default is '45'.
    atm : str
        The atmosphere in percentile. Default is '50'.

    Returns
    -------
    psf : np.ndarray
        The PSF image.
    info : dict
        The PSF info from the header.
    """
    filename = _get_iris_psf_filename(
        mode,
        xs=xs, ys=ys,
        itime=itime,
        zenith=zenith,
        atm=atm,
    )
    filepath = os.path.join(_get_iris_psf_dir(), filename)
    psf, info = _read_iris_psf(filepath, wave=wave)
    info['mode'] = mode
    return psf, info
    

def _get_iris_psf_filename(
    mode : str,
    xs : float = 0, ys : float = 0,
    itime : float = 300,
    zenith : str = '45', atm : str = '50',
) -> str:
    """
    Gets the filename of the PSF for the imager or IFS.

    Parameters
    ----------
    mode: str
        The mode ('img', 'ifs').
    xs : float
        The x offset in arcsec from on-axis.
    ys : float
        The y offset in arcsec from on-axis.
    itime : float
        The integration time in seconds.
    zenith : str
        The zenith angle in degrees.
    atm : str
        The atmosphere in percentile.

    Returns
    -------
    filename : str
        The filename of the PSF.
    """

    # Resolve input params
    mode = mode.lower()
    itimes = np.array([1.4, 300])
    k = np.argmin(np.abs(itimes - itime))
    itime = itimes[k]
    if itime == int(itime):
        itime = int(itime)
    zenith = int(zenith)

    # Determine filename based on input parameters
    if mode == 'img':
        xs_ao = np.array([0.6, 4.7, 8.8, 12.9, 17])
        ys_ao = np.array([0.6, 4.7, 8.8, 12.9, 17])
        xs = xs_ao[np.argmin(np.abs(xs_ao - xs))]
        ys = xs_ao[np.argmin(np.abs(ys_ao - ys))]
        if xs == int(xs):
            xs = int(xs)
        if ys == int(ys):
            ys = int(ys)
        filename = f"za{zenith}_{int(atm)}p_im_{itime}s{os.sep}evlpsfcl_1_x{xs}_y{ys}_2mas.fits"
    elif mode == 'ifs':
        filename = f"za{zenith}_{int(atm)}p_ifu_{itime}s{os.sep}evlpsfcl_1_x0_y0_2mas.fits"
    else:
        raise ValueError(f"Unknown mode '{mode}'.")
    return filename


def _read_iris_psf(
    filepath : str,
    hdunum : int | None = None,
    wave : float | None = None
) -> tuple[np.ndarray, dict]:
    """
    Read the IRIS PSF file and return the PSF array and metadata.
    """
    if hdunum is None:
        hdunum = _get_iris_psf_hdu_for_wavelength(filepath, wave)
    with fits.open(filepath) as hdulist:
        psf = hdulist[hdunum].data
        psf = to_little_endian(psf)
        info = _parse_iris_psf_header(hdulist[hdunum].header)
        info['filename'] = filepath
        info['hdunum'] = hdunum
        info['atm'] = filepath.split('/')[-2][2:4]
        info['weather'] = filepath.split('/')[-2][5:7]
    return psf, info


def _get_iris_psf_hdu_for_wavelength(filepath : str, wave : float) -> int:
    """
    Get the HDU number for a given wavelength in microns.
    """
    with fits.open(filepath) as hdulist:
        waves = np.full(len(hdulist), np.nan)
        for i in range(len(hdulist)):
            header = hdulist[i].header
            info = _parse_iris_psf_header(header)
            waves[i] = info['wavelength']
        hdunum = np.argmin(np.abs(waves - wave))
    return hdunum


def _parse_iris_psf_header(header : fits.Header) -> dict:
    """
    Parse the header of a PSF file.
    """

    # Split into a list
    comments = ""
    for comment in header['COMMENT']:
        comments += comment.strip()
    comments = comments.split(';')
    # Result
    info = {}

    # Position
    match = re.search(r'Science PSF at \(([\d.]+),\s*([\d.]+)\)\s*arcsec', comments[0])
    info['x'] = match[1]
    info['y'] = match[2]

    # r0
    match = re.search(r'r0=([\d.]+)', comments[1])
    info['r0'] = float(match[1])

    # l0
    match = re.search(r'l0=([\d.]+)', comments[1])
    info['l0'] = float(match[1])

    # wavelength
    match = re.search(r'Wavelength:\s*([\d.eE+-]+)m', comments[2])
    info['wavelength'] = 1E6 * float(match[1]) # convert meters to microns

    # OPD sampling
    match = re.search(r'OPD Sampling:\s*([\d.]+)m', comments[3])
    info['opd_sampling'] = 1E6 * float(match[1]) # convert meters to microns

    # fft grid
    match = re.search(r'FFT Grid:\s*(\d+)x(\d+)', comments[4])
    info['fft_grid'] = (int(match[1]), int(match[2]))

    # psf sampling
    match = re.search(r'PSF Sampling:\s*([\d.eE+-]+)\s*arcsec', comments[5])
    info['psf_sampling'] = float(match[1]) # arcsec

    # Sum
    match = re.search(r'PSF Sum to:\s*([\d.eE+-]+)', comments[6])
    info['sum'] = float(match[1])

    # itime
    match = re.search(r'Exposure:\s*(\d+)s', comments[7])
    info['itime'] = float(match[1])
    
    return info
