import importlib.resources
import numpy as np

__all__ = ['load_throughputs']

def load_throughputs(
    instrument : str,
    mode : str | None,
    ifs_mode : str | None = None,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """
    Load the appropriate throughput samples for this instrument.

    Returns
    -------
    dict
        A dictionary containing the throughput curves for each mode and instrument.
    """
    instrument = instrument.lower()
    if instrument == 'liger':
        return _load_liger_throughputs(mode, ifs_mode)
    elif instrument == 'iris':
        return _load_iris_throughputs(mode, ifs_mode)

###########################
#### Liger Throughputs ####
###########################

def _get_liger_throughput_filename(mode : str, ifs_mode : str | None) -> str:
    if mode.lower() == 'img':
        return 'liger_imager_tput.txt'
    elif mode.lower() == 'ifs':
        ifs_mode = ifs_mode.lower()
        if ifs_mode == 'slicer':
            return 'liger_slicer_tput.txt'
        elif ifs_mode == 'lenslet':
            return 'liger_lenslet_tput.txt'
        else:
            raise ValueError(f"Invalid ifs_mode {ifs_mode=}")
    else:
        raise ValueError(f"Invalid mode {mode=}")


def _load_liger_throughputs(
    mode : str,
    ifs_mode : str | None
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load the Liger throughput curve for the specified modes.

    Parameters
    ----------
    mode : str
        The mode ('imager', 'ifs').
    ifs_mode : str | None
        The IFS mode ('slicer', 'lenslet') if mode is 'ifs'.
    
    Returns
    -------
    waves_tput : np.ndarray
        The wavelengths in microns where the throughput is sampled.
    inst_tput : np.ndarray
        The instrument throughput at each wavelength.
    """
    filename = _get_liger_throughput_filename(mode, ifs_mode)
    filepath = importlib.resources.files('liger_iris_drp_resources') / f'resources/throughput/{filename}'
    waves_tput, inst_tput = np.loadtxt(filepath, delimiter=',', unpack=True, skiprows=1)
    return waves_tput, inst_tput


##########################
#### IRIS Throughputs ####
##########################

def _get_iris_throughput_filename(mode : str) -> str:
    if mode.lower() == 'img':
        return 'iris_imager_tput.txt'
    elif mode.lower() == 'ifs':
        return 'iris_ifs_tput.txt'
    else:
        raise ValueError(f"Invalid mode {mode=}")

def _load_iris_throughputs(
    mode : str,
    ifs_mode : str | None = None # NOTE: Probably eventually used, so keep for consitent interface
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load the IRIS throughput curve for the specified modes.

    Parameters
    ----------
    mode : str
        The mode ('imager', 'ifs').
    ifs_mode : str | None
        The IFS mode ('slicer', 'lenslet') if mode is 'ifs'.

    Returns
    -------
    waves_tput : np.ndarray
        The wavelengths in microns where the throughput is sampled.
    inst_tput : np.ndarray
        The instrument throughput at each wavelength.
    """
    filename = _get_iris_throughput_filename(mode)
    filepath = importlib.resources.files('liger_iris_drp_resources') / f'resources/throughput/{filename}'
    waves_tput, inst_tput = np.loadtxt(filepath, delimiter=',', unpack=True, skiprows=1)
    return waves_tput, inst_tput