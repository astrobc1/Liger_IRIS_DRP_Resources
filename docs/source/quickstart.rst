Quickstart
==========

Ensure you have followed the :doc:`installation instructions <../installation>` before proceeding with this quickstart guide.

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
    print(filters["K"])
    # -> {'filter': np.str_('K'), 'wavemin': np.float64(2.0), 'wavecenter': np.float64(2.2), 'wavemax': np.float64(2.4), 'bandwidth': np.float64(0.4), 'backmag': np.float64(15.1028), 'zpphot': np.float64(4564590399.386499), 'transmission_file': np.str_('iris_filter_K.txt')}


Filter transmission curves are downloaded from the Google Drive.

.. code-block:: python

    from liger_iris_drp_resources.filters import download_filter_transmission_curves, load_filter_transmission_curve

    # Transmission curve for a specific filter
    wave, trans = load_filter_transmission_curve("K")


Gratings
--------

A summary table of the IFS gratings is included with the package.

.. code-block:: python

    from liger_iris_drp_resources.gratings import load_gratings_summary

    gratings = load_gratings_summary()
    print(gratings["K4000"])
    # -> {'grating': np.str_('K4000'), 'groov_density': np.int64(151), 'resolution': np.int64(4000), 'alpha': np.float64(10.3), 'dimension': np.float64(32.801), 'wavemin': np.float64(1.975), 'wavemax': np.float64(2.412), 'wavecenter': np.float64(2.1825)}


Model Spectra
-------------

Model spectra are hosted on Google Drive.
The data simulator and pipeline use specific files stored here.

.. code-block:: python

    from liger_iris_drp_resources.model_spectra import download_model_spectra

    download_model_spectra()
    # Files are saved to /path/to/resources/Model_Spectra/


PSFs
----

Liger PSFs are hosted on Google Drive as a zip archive.

**IRIS PSFs are only available when running code on the Galactica cluster where IRIS PSFs are stored.**

.. code-block:: python

    from liger_iris_drp_resources.psfs import load_liger_psf

    # Load the PSF closest to 1248 nm at position (0", 0")
    psf, info = load_liger_psf(
        instrument_mode='img', # Instrument mode: 'img' or 'ifs'
        wave=1.248, # Wavelength in microns
        xdet=1024, ydet=1024, # Detector coords
    )

.. code-block:: python

    from liger_iris_drp_resources.psfs import load_iris_psf
    
    psf, info = load_iris_psf(
        instrument_mode='img',
        wave=1.65,
        xdet=1024,
        ydet=1024,
        itime=300,
        zenith='45',
        atm='50'
    )

Micropupils
-----------

Liger and IRIS lenslet micropupil files are hosted on Google Drive as a zip archive.

.. code-block:: python

    from liger_iris_drp_resources.micropupils import load_micropupil_for_filter

    # Load the micropupil for the K filter
    mp, filepath = load_micropupil_for_filter(filter_name='KN2')