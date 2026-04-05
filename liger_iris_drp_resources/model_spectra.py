import os
import gdown

from .utils import get_resource_dir

import logging
logger = logging.getLogger(__name__)

def _get_model_spectra_dir() -> str:
    return os.path.join(get_resource_dir(), 'Model_Spectra')

def download_model_spectra(output_dir: str | None = None) -> str:
    """
    Download Model spectra from a Google Drive folder.

    Parameters
    ----------
    output_dir :  str | None
        The directory to download the files to.
        If None, a default directory will be used.

    Returns:
        str: The path to the downloaded files.
    """
    if output_dir is None:
        output_dir = _get_model_spectra_dir()

    os.makedirs(output_dir, exist_ok=True)

    model_spectra_url = 'https://drive.google.com/drive/folders/1aWN7B4IMsG2c6lV9WVNY3qWsq5C_YIKi?usp=drive_link'

    print(f"Downloading Model spectra to {output_dir}...")

    try:
        files = gdown.download_folder(
            url=model_spectra_url,
            output=output_dir,
            quiet=False,
        )

        if not files:
            msg = "Failed to download Model spectra: no files returned"
            logger.error(msg)
            raise RuntimeError(msg)

        if not os.listdir(output_dir):
            msg = f"Download completed but directory is empty: {output_dir}"
            logger.error(msg)
            raise RuntimeError(msg)

        logger.info(f"Successfully downloaded Model spectra to {output_dir}")
        return output_dir

    except Exception as e:
        logger.error(f"Failed to download Model spectra: {e}")
        raise RuntimeError("Model spectra download failed") from e