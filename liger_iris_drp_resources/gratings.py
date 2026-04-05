import importlib.resources
import numpy as np

__all__ = ['load_gratings_summary']

def load_gratings_summary() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """
    Loads the gratings summary file.

    Returns
    -------
    dict
        A dictionary containing information for each grating.
        Keys are grating names.
        Values are dictionaries with grating information.
    """
    filename = 'gratings_summary.txt'
    filepath = importlib.resources.files('liger_iris_drp_resources') / f'resources/gratings/{filename}'
    data = np.genfromtxt(filepath, dtype=None, names=True, delimiter=',', encoding='utf-8')
    out = {}
    for i, filt in enumerate(data['grating']):
        out[filt] = {key : data[key][i] for key in data.dtype.names}
    return out