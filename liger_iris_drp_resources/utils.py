import os
from astropy.utils.data import _get_download_cache_loc

import logging
logger = logging.getLogger(__name__)

def get_resource_dir():
    resource_dir = os.getenv('LIGER_IRIS_DRP_RESOURCE_DIR')
    if resource_dir is None:
        resource_dir = os.path.join(
            str(_get_download_cache_loc()),
            'LIGER_IRIS_DRP_RESOURCE_DIR',
        )
    return resource_dir