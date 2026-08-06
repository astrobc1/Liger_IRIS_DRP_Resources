import importlib.resources
import astropy.io.fits as fits
import numpy as np
import os
import gdown
import zipfile
import astropy.time

from .utils import get_resource_dir

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'download_micropupils',
    'load_micropupil_for_filter'
]

def get_micropupil_filename(filter_name : str | None = None) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """
    Loads the micropupil filename map.

    Parameters
    ----------
    filter_name : str | None
        The filter name to retrieve the micropupil filename for.
        If None, returns a dict of all filter names and their corresponding micropupil filenames.

    Returns
    -------
    dict
        A dictionary mapping filter names to their corresponding micropupil filenames.
    """
    filename = 'micropupil_filemap.txt'
    filepath = importlib.resources.files('liger_iris_drp_resources') / f'resources/micropupils/{filename}'
    data = np.genfromtxt(filepath, dtype=None, names=True, delimiter=',', encoding='utf-8')
    
    out = {}
    for filt, mp_file in zip(data['filter'], data['micropupil_file']):
        out[filt] = mp_file

    if filter_name is not None:
        return out[filter_name]
    return out

def _get_micropupils_dir() -> str:
    return os.path.join(get_resource_dir(), 'micropupils')

def download_micropupils(
    output_dir: str | None = None,
    skip_if_exists: bool = True
) -> str:
    """
    Download the micropupils from Google Drive.

    Parameters
    ----------
    output_dir : str | None
        The directory to save the micropupils to.
    skip_if_exists : bool
        If True, skip downloading if the output directory already exists and is not empty.
        Default is True.

    Returns
    -------
    str
        The directory containing the downloaded micropupils.
    """
    if output_dir is None:
        output_dir = _get_micropupils_dir()

    if skip_if_exists and os.path.exists(output_dir) and any(os.listdir(output_dir)):
        logger.info(f"Micropupils already exist at {output_dir}, skipping download.")
        return output_dir

    os.makedirs(output_dir, exist_ok=True)

    url = 'https://drive.google.com/file/d/1wg_XNe8SmIVZC5kNd9w9FrWUk2ZHm7FN/view?usp=drive_link'
    timestamp = astropy.time.Time.now().iso.replace(":", "-").replace(".", "-")
    temp_zip = os.path.join(output_dir, f"micropupils_{timestamp}.zip")

    logger.info(f"Downloading micropupils to {output_dir}...")

    gdown.download(url=url, output=temp_zip, quiet=False)

    if not os.path.exists(temp_zip):
        msg = f"Failed to download micropupils: file not found at {temp_zip}"
        logger.error(msg)
        raise RuntimeError(msg)

    try:
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            extracted_files = zip_ref.namelist()

            if not extracted_files:
                msg = "Downloaded micropupil zip archive is empty"
                logger.error(msg)
                raise RuntimeError(msg)

            # Filter out macOS metadata and hidden entries before extracting
            members = [
                f for f in extracted_files
                if 'MACOSX' not in f and not f.startswith('.')
            ]
            zip_ref.extractall(output_dir, members=members)

        logger.info(f"Successfully downloaded and extracted micropupils to {output_dir}")
        return output_dir

    except zipfile.BadZipFile as e:
        logger.error(f"Downloaded file {temp_zip} is not a valid zip archive: {e}")
        raise RuntimeError("Invalid zip archive for micropupils")from e
    finally:
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

def load_micropupil_for_filter(filter_name : str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load the micropupil for a filter.

    Parameters
    ----------
    filter_name : str
        The filter name.

    Returns
    -------
    mp : np.ndarray
        The micropupil for the filter, oversampled by 15x and not convolved by the pixel response_function.
    filepath : str
        The path to the micropupil file that was loaded.
    """
    mp_dir = _get_micropupils_dir()
    filename = get_micropupil_filename(filter_name)
    filepath = os.path.join(mp_dir, filename)
    mp = fits.getdata(filepath, ext=0)
    return mp