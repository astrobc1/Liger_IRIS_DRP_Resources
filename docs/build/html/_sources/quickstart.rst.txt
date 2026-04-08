Quickstart
==========

Ensure you have followed the :doc:`installation instructions <../installation>` before proceeding with this quickstart guide.

If any example below requires data from the `Link to Google Drive folder <https://drive.google.com/drive/folders/15vSPi9QRine2F2zhZ7xeSXJF7fMXZdoe?usp=drive_link>`_, it will automatically download the necessary files to the local resources directory.

Examples below assume the user has set the environment variable **LIGER_IRIS_DRP_RESOURCE_DIR** to a valid directory path, or is using the default resources directory.


Throughput
----------

Instrument throughput curves map wavelength (in microns) to fractional throughput for the imager and IFS modes.

Instrument throughputs are sampled at several wavelengths across the bandpass.

These values do **not** include the filter transmission.

These are directly included with the package:

.. code-block:: python

    from liger_iris_drp_resources.throughput import load_throughputs

    # Liger imager
    waves, tput = load_throughputs("liger", "img")

    # Liger IFS (slicer or lenslet)
    waves, tput = load_throughputs("liger", "ifs", "slicer")
    waves, tput = load_throughputs("liger", "ifs", "lenslet")

    # IRIS imager or IFS
    waves, tput = load_throughputs("iris", "img")
    waves, tput = load_throughputs("iris", "ifs")

Both ``waves`` and ``tput`` are numpy arrays.


Filters
-------

A summary table of the filters is included with the package.

.. code-block:: python

    from liger_iris_drp_resources.filters import load_filters_summary

    # Summary table — dict keyed by filter name
    filters = load_filters_summary()
    print(filters["K"])  # e.g. {'filter': 'K', 'lambda_min': ..., 'lambda_max': ..., ...}


Filter transmission curves are downloaded from the Google Drive.

.. code-block:: python

    from liger_iris_drp_resources.filters import download_filter_transmission_curves, load_filter_transmission_curve

    # Download filter transmission curves
    download_filter_transmission_curves()

    # Transmission curve for a specific filter
    wave, trans = load_filter_transmission_curve("K")


Gratings
--------

A summary table of the IFS gratings is included with the package.

.. code-block:: python

    from liger_iris_drp_resources.gratings import load_gratings_summary

    gratings = load_gratings_summary()
    print(gratings["K4000"])
    # {'grating': 'K4000', 'groov_density': 151, 'resolution': 4000,
    #  'wavemin': 1.975, 'wavemax': 2.412, 'wavecenter': 2.1825, ...}


Model Spectra
-------------

Model spectra are hosted on Google Drive.

.. code-block:: python

    from liger_iris_drp_resources.model_spectra import download_model_spectra

    download_model_spectra()
    # Files are saved to /path/to/resources/Model_Spectra/


PSFs
----

Liger PSFs are hosted on Google Drive as a zip archive.

IRIS PSFs are not yet available.

.. code-block:: python

    from liger_iris_drp_resources.psfs import download_liger_psfs, load_liger_psf

    download_liger_psfs()

    # Load the PSF closest to 1248 nm at position (0", 0")
    psf, info = load_liger_psf(wave=1248, xs=0, ys=0)