import importlib.resources
import numpy as np
import os
import gdown
import zipfile
import astropy.time

from .utils import get_resource_dir

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'download_filter_transmission_curves',
    'load_filters_summary',
    'load_filter_transmission_curve'
]

def load_filters_summary(filter_name : str | None = None) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """
    Loads the filters summary file.

    Parameters
    ----------
    filter_name : str | None
        The filter name to load. If None, loads all filters.

    Returns
    -------
    dict
        A dictionary containing information for each filter.
        Keys are filter names.
        Values are dictionaries with filter information.
    """
    filename = 'filters_summary.txt'
    filepath = importlib.resources.files('liger_iris_drp_resources') / f'resources/filters/{filename}'
    data = np.genfromtxt(filepath, dtype=None, names=True, delimiter=',', encoding='utf-8')
    
    out = {}
    for i, filt in enumerate(data['filter']):
        out[filt] = {key : data[key][i] for key in data.dtype.names}

    if filter_name is not None:
        return out[filter_name]
    return out

def _get_filter_transmission_curves_dir() -> str:
    return os.path.join(get_resource_dir(), 'Filters')

def download_filter_transmission_curves(
    output_dir: str | None = None,
    skip_if_exists: bool = True
) -> str:
    """
    Download the filter transmission curves from Google Drive.

    Parameters
    ----------
    output_dir : str | None
        The directory to save the transmission curves to.
    skip_if_exists : bool
        If True, skip downloading if the output directory already exists and is not empty.
        Default is True.

    Returns
    -------
    str
        The directory containing the downloaded filter transmission curves.
    """
    if output_dir is None:
        output_dir = _get_filter_transmission_curves_dir()

    if skip_if_exists and os.path.exists(output_dir) and any(os.listdir(output_dir)):
        logger.info(f"Filter transmission curves already exist at {output_dir}, skipping download.")
        return output_dir

    os.makedirs(output_dir, exist_ok=True)

    url = 'https://drive.google.com/file/d/1C27Eo2XqrIZz1q0Rw7pvuOydVhjxiedy/view?usp=drive_link'
    timestamp = astropy.time.Time.now().iso.replace(":", "-").replace(".", "-")
    temp_zip = os.path.join(output_dir, f"filter_transmission_curves_{timestamp}.zip")

    logger.info(f"Downloading filter transmission curves to {output_dir}...")

    gdown.download(url=url, output=temp_zip, quiet=False, fuzzy=True)

    if not os.path.exists(temp_zip):
        msg = f"Failed to download filter transmission curves: file not found at {temp_zip}"
        logger.error(msg)
        raise RuntimeError(msg)

    try:
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            extracted_files = zip_ref.namelist()

            if not extracted_files:
                msg = "Downloaded filter transmission curve zip archive is empty"
                logger.error(msg)
                raise RuntimeError(msg)

            # Filter out macOS metadata and hidden entries before extracting
            members = [
                f for f in extracted_files
                if 'MACOSX' not in f and not f.startswith('.')
            ]
            zip_ref.extractall(output_dir, members=members)

        logger.info(f"Successfully downloaded and extracted filter transmission curves to {output_dir}")
        return output_dir

    except zipfile.BadZipFile as e:
        logger.error(f"Downloaded file {temp_zip} is not a valid zip archive: {e}")
        raise RuntimeError("Invalid zip archive for filter transmission curves") from e
    finally:
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

def load_filter_transmission_curve(filter_name : str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load the transmission curve for a filter.

    Parameters
    ----------
    filter_name : str
        The filter name.

    Returns
    -------
    wave : np.ndarray
        The wavelength grid (microns).
    trans : np.ndarray
        The transmission curve (0-1).
    """
    trans_dir = _get_filter_transmission_curves_dir()
    filename = f'iris_filter_trans_{filter_name}.txt'
    filepath = os.path.join(trans_dir, filename)
    wave, trans = np.loadtxt(filepath, delimiter=',', unpack=True)
    return wave, trans