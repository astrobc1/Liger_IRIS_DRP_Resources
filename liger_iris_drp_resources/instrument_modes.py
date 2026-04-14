import re
import numpy as np
import os
import astropy.table

from .filters import load_filters_summary

__all__ = [
    'make_liger_modes_table',
    'make_iris_modes_table'
]

gratings_lenslet = [
    'Z4000', 'Y4000', 'J4000', 'H4000', 'K4000', 'YJ4000', 'HK4000',
    'Z8000', 'Y8000', 'J8000', 'H8000', 'K8000', 'K8000a', 'K8000b',
    'H10000', 'K10000'
]

gratings_slicer = [
    'Z4000', 'Y4000', 'J4000', 'H4000', 'K4000', 'YJ4000', 'HK4000',
    'Z8000', 'Y8000', 'J8000', 'H8000', 'K8000a', 'K8000b'
]

modes = ['IMG', 'IFS']
ifs_modes = ['SLICER', 'LENSLET']

def get_fov(size, plate_scale, decimals=2):
    return (
        np.round(size[0] * plate_scale / 1000, decimals=decimals),
        np.round(size[1] * plate_scale / 1000, decimals=decimals)
    )

COLUMNS = {
    'MODE': 'U10',
    'IFS_MODE': 'U10',
    'GRATING': 'U10',
    'PLATE_SCALE': 'f4',
    'FILTER': 'U20',
    'FOV': object,
    'NUM_SPATIAL_ELEMENTS': object,
    'SPECTRAL_RESOLUTION': object,
    'WAVEMIN': 'f4',
    'WAVECEN': 'f4',
    'WAVEMAX': 'f4',
    'BANDWIDTH': 'f4',
}

def make_empty_table():
    t = astropy.table.Table()
    for k, dt in COLUMNS.items():
        t[k] = np.array([], dtype=dt)
    return t

def make_liger_modes_table():

    # Filter summary
    fd = load_filters_summary()

    # NOTE: YN4 is missing from filter_info.dat file but is on the TMT ETC
    # NOTE: KN4.5 is missing from filter_info.dat file but is on the TMT ETC
    filter_names_imager = [
        'Zbb', 'Ybb', 'Jbb', 'Hbb', 'Kbb',
        'Z', 'Y', 'J', 'H', 'Ks', 'K',
        'ZN1', 'ZN2', 'ZN3', 'ZN4',
        'YN1', 'YN2', 'YN3', #'YN4',
        'JN1', 'JN2', 'JN3', 'JN4',
        'HN1', 'HN2', 'HN3', 'HN4', 'HN5',
        'KN1', 'KN2', 'KN3', 'KN4', 'KN5',
        'CaIIw', 'PaBetaw', 'FeIIw', 'Br_Gammaw', 'COw', 'HeI', 'Jcont', 'PaBeta', 'Hcont', 'FeII', 'H2one', 'Kcont', 'Br_Gamma', 'H2two', 'CO'
    ]

    # NOTE: YN4 is missing from filter_info.dat file but is on the TMT ETC
    # NOTE: KN4.5 is missing from filter_info.dat file but is on the TMT ETC
    filter_names_ifs = [
        'Zbb', 'Ybb', 'Jbb', 'Hbb', 'Kbb',
        'Z', 'Y', 'J', 'H', 'Ks', 'K',
        'ZN1', 'ZN2', 'ZN3', 'ZN4',
        'YN1', 'YN2', 'YN3', # 'YN4',
        'JN1', 'JN2', 'JN3', 'JN4',
        'HN1', 'HN2', 'HN3', 'HN4', 'HN5',
        'KN1', 'KN2', 'KN3', 'KN4', 'KN5',
    ]

    # Pixels
    detector_size_imager = (2048, 2048)

    # mas
    plate_scale_imager = 10
    plate_scales_lenslet = [14, 31]
    plate_scales_slicer = [75, 150]

    # arcsec
    fov_imager = (
        np.round(detector_size_imager[0] * plate_scale_imager / 1000, decimals=2), np.round(detector_size_imager[1] * plate_scale_imager / 1000, decimals=2)
    )

    ################################
    #### IMAGER modes for Liger ####
    ################################
    rows = []
    for filt in filter_names_imager:
        rows.append({
            'MODE' : 'IMG',
            'IFS_MODE' : 'None',
            'GRATING' : 'None',
            'PLATE_SCALE' : plate_scale_imager,
            'FILTER' : filt,
            'FOV' : fov_imager,
            'NUM_SPATIAL_ELEMENTS' : detector_size_imager,
            'SPECTRAL_RESOLUTION' : 'None',
            'WAVEMIN' : fd[filt]['wavemin'],
            'WAVECEN' : fd[filt]['wavecenter'],
            'WAVEMAX' : fd[filt]['wavemax'],
            'BANDWIDTH' : fd[filt]['bandwidth']
        })


    modes_imager = make_empty_table()
    for row in rows:
        modes_imager.add_row(row)

    #################################
    #### LENSLET modes for Liger ####
    #################################
    rows = []
    for grating in gratings_lenslet:
        resolution = float(re.search(r'\d+\.?\d*', grating).group())
        band = grating[0]
        if resolution == 10000:
            filts = [filt for filt in filter_names_ifs if filt.startswith(band) and 'bb' in filt]
        else:
            filts = [filt for filt in filter_names_ifs if filt.startswith(band)]
        for filt in filts:
            for plate_scale in plate_scales_lenslet:
                if resolution == 4000:
                    size = (16, 128) if 'bb' in filt else (112, 128)
                elif resolution == 8000:
                    size = (16, 128)
                elif resolution == 1000:
                    size = (16, 128)
                fov = get_fov(size, plate_scale)
                rows.append({
                    'MODE' : 'IFS',
                    'IFS_MODE' : 'LENSLET',
                    'GRATING' : grating,
                    'PLATE_SCALE' : plate_scale,
                    'FILTER' : filt,
                    'FOV' : fov,
                    'NUM_SPATIAL_ELEMENTS' : size,
                    'SPECTRAL_RESOLUTION' : resolution,
                    'WAVEMIN' : fd[filt]['wavemin'],
                    'WAVECEN' : fd[filt]['wavecenter'],
                    'WAVEMAX' : fd[filt]['wavemax'],
                    'BANDWIDTH' : fd[filt]['bandwidth']
                })

    ## Add YJ, HK mode for LENSLET
    #16 x 128
    #44 x 88

    # YJ LENSLET SCALE = 14 mas
    plate_scale = 14
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })

    # YJ LENSLET SCALE = 31 mas
    plate_scale = 31
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })


    # HK LENSLET SCALE = 14 mas
    plate_scale = 14
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    # HK LENSLET SCALE = 31 mas
    plate_scale = 31
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    modes_lenslet = make_empty_table()
    for row in rows:
        modes_lenslet.add_row(row)

    ################################
    #### SLICER modes for Liger ####
    ################################
    rows = []
    for grating in gratings_slicer:
        resolution = float(re.search(r'\d+\.?\d*', grating).group())
        band = grating[0]
        filts = [filt for filt in filter_names_ifs if filt.startswith(band)]
        for filt in filts:
            for plate_scale in plate_scales_slicer:
                if resolution == 4000:
                    size = (44, 45) if 'bb' in filt else (88, 45)
                elif resolution == 8000:
                    size = (44, 45)
                fov = get_fov(size, plate_scale)
                rows.append({
                    'MODE' : 'IFS',
                    'IFS_MODE' : 'SLICER',
                    'GRATING' : grating,
                    'PLATE_SCALE' : plate_scale,
                    'FILTER' : filt,
                    'FOV' : fov,
                    'NUM_SPATIAL_ELEMENTS' : size,
                    'SPECTRAL_RESOLUTION' : resolution,
                    'WAVEMIN' : fd[filt]['wavemin'],
                    'WAVECEN' : fd[filt]['wavecenter'],
                    'WAVEMAX' : fd[filt]['wavemax'],
                    'BANDWIDTH' : fd[filt]['bandwidth']
                })


    # YJ SLICER SCALE = 45 mas
    plate_scale = 45
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })

    # YJ SLICER SCALE = 88 mas
    plate_scale = 88
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })


    # HK SLICER SCALE = 45 mas
    plate_scale = 45
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    # HK SLICER SCALE = 88 mas
    plate_scale = 88
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    modes_slicer = make_empty_table()
    for row in rows:
        modes_slicer.add_row(row)

    modes_all = astropy.table.vstack((modes_imager, modes_lenslet, modes_slicer))

    return modes_all


def make_iris_modes_table():

    # Filter summary
    fd = load_filters_summary()

    filter_names_imager = [
        'Zbb', 'Ybb', 'Jbb', 'Hbb', 'Kbb',
        'Z', 'Y', 'J', 'H', 'Ks', 'K',
        'ZN1', 'ZN2', 'ZN3', 'ZN4',
        'YN1', 'YN2', 'YN3', 'YN4',
        'JN1', 'JN2', 'JN3', 'JN4',
        'HN1', 'HN2', 'HN3', 'HN4', 'HN5',
        'KN1', 'KN2', 'KN3', 'KN4', 'KN5',
        'CaIIw', 'PaBetaw', 'FeIIw', 'Br_Gammaw', 'COw', 'HeI', 'Jcont', 'PaBeta', 'Hcont', 'FeII', 'H2one', 'Kcont', 'Br_Gamma', 'H2two', 'CO'
    ]

    filter_names_ifs = [
        'Zbb', 'Ybb', 'Jbb', 'Hbb', 'Kbb',
        'Z', 'Y', 'J', 'H', 'Ks', 'K',
        'ZN1', 'ZN2', 'ZN3', 'ZN4',
        'YN1', 'YN2', 'YN3', 'YN4',
        'JN1', 'JN2', 'JN3', 'JN4',
        'HN1', 'HN2', 'HN3', 'HN4', 'HN5',
        #'KN1', 'KN2', 'KN3', 'KN4', 'KpN45', 'KN5',
        'KN1', 'KN2', 'KN3', 'KN4', 'KN5',
    ]

    # Pixels
    detector_size_imager = (4096, 4096)

    # mas
    plate_scale_imager = 4
    plate_scales_lenslet = [4, 9]
    plate_scales_slicer = [25, 50]

    # arcsec
    fov_imager = (
        np.round(detector_size_imager[0] * plate_scale_imager / 1000, decimals=2), np.round(detector_size_imager[1] * plate_scale_imager / 1000, decimals=2)
    )

    ###############################
    #### IMAGER modes for IRIS ####
    ###############################
    rows = []
    for filt in filter_names_imager:
        rows.append({
            'MODE' : 'IMG',
            'IFS_MODE' : 'None',
            'GRATING' : 'None',
            'PLATE_SCALE' : plate_scale_imager,
            'FILTER' : filt,
            'FOV' : fov_imager,
            'NUM_SPATIAL_ELEMENTS' : detector_size_imager,
            'SPECTRAL_RESOLUTION' : 'None',
            'WAVEMIN' : fd[filt]['wavemin'],
            'WAVECEN' : fd[filt]['wavecenter'],
            'WAVEMAX' : fd[filt]['wavemax'],
            'BANDWIDTH' : fd[filt]['bandwidth']
        })

    modes_imager = make_empty_table()
    for row in rows:
        modes_imager.add_row(row)


    ################################
    #### LENSLET modes for IRIS ####
    ################################
    rows = []
    for grating in gratings_lenslet:
        resolution = float(re.search(r'\d+\.?\d*', grating).group())
        band = grating[0]
        if resolution == 10000:
            filts = [filt for filt in filter_names_ifs if filt.startswith(band) and 'bb' in filt]
        else:
            filts = [filt for filt in filter_names_ifs if filt.startswith(band)]
        if grating == 'K8000a':
            filts = ['KN1', 'KN2', 'KN3', 'Kbb']
        if grating == 'K8000b':
            #filts = ['KN4', 'KN4.5', 'KN5', 'Kbb']
            filts = ['KN4', 'KN5', 'Kbb']
        for filt in filts:
            for plate_scale in plate_scales_lenslet:
                if resolution == 4000:
                    size = (16, 128) if 'bb' in filt else (112, 128)
                elif resolution == 8000:
                    size = (16, 128)
                elif resolution == 10000:
                    size = (16, 128)
                fov = get_fov(size, plate_scale)
                rows.append({
                    'MODE' : 'IFS',
                    'IFS_MODE' : 'LENSLET',
                    'GRATING' : grating,
                    'PLATE_SCALE' : plate_scale,
                    'FILTER' : filt,
                    'FOV' : fov,
                    'NUM_SPATIAL_ELEMENTS' : size,
                    'SPECTRAL_RESOLUTION' : resolution,
                    'WAVEMIN' : fd[filt]['wavemin'],
                    'WAVECEN' : fd[filt]['wavecenter'],
                    'WAVEMAX' : fd[filt]['wavemax'],
                    'BANDWIDTH' : fd[filt]['bandwidth']
                })

    ## Add YJ, HK mode for LENSLET
    #16 x 128
    #44 x 88

    # YJ LENSLET SCALE = 4 mas
    plate_scale = 4
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })

    # YJ LENSLET SCALE = 9 mas
    plate_scale = 9
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })


    # HK LENSLET SCALE = 4 mas
    plate_scale = 4
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    # HK LENSLET SCALE = 9 mas
    plate_scale = 9
    size = (16, 128)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'LENSLET',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    modes_lenslet = make_empty_table()
    for row in rows:
        modes_lenslet.add_row(row)

    ###############################
    #### SLICER modes for IRIS ####
    ###############################
    rows = []
    for grating in gratings_slicer:
        resolution = float(re.search(r'\d+\.?\d*', grating).group())
        band = grating[0]
        filts = [filt for filt in filter_names_ifs if filt.startswith(band)]
        for filt in filts:
            for plate_scale in plate_scales_slicer:
                if resolution == 4000:
                    size = (44, 45) if 'bb' in filt else (88, 45)
                elif resolution == 8000:
                    size = (44, 45)
                fov = (
                    np.round(size[0] * plate_scale / 1000, decimals=2),
                    np.round(size[1] * plate_scale / 1000, decimals=2)
                )
                rows.append({
                    'MODE' : 'IFS',
                    'IFS_MODE' : 'SLICER',
                    'GRATING' : grating,
                    'PLATE_SCALE' : plate_scale,
                    'FILTER' : filt,
                    'FOV' : fov,
                    'NUM_SPATIAL_ELEMENTS' : size,
                    'SPECTRAL_RESOLUTION' : resolution,
                    'WAVEMIN' : fd[filt]['wavemin'],
                    'WAVECEN' : fd[filt]['wavecenter'],
                    'WAVEMAX' : fd[filt]['wavemax'],
                    'BANDWIDTH' : fd[filt]['bandwidth']
                })


    # YJ SLICER SCALE = 25 mas
    plate_scale = 25
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })

    # YJ SLICER SCALE = 50 mas
    plate_scale = 50
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'YJ4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'YJ',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 0.925,
        'WAVECEN' : 1.1325,
        'WAVEMAX' : 1.34,
        'BANDWIDTH' : 1.34 - 0.925 
    })


    # HK SLICER SCALE = 25 mas
    plate_scale = 25
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    # HK SLICER SCALE = 50 mas
    plate_scale = 50
    size = (88, 45)
    fov = get_fov(size, plate_scale)
    rows.append({
        'MODE' : 'IFS',
        'IFS_MODE' : 'SLICER',
        'GRATING' : 'HK4000',
        'PLATE_SCALE' : plate_scale,
        'FILTER' : 'HK',
        'FOV' : fov,
        'NUM_SPATIAL_ELEMENTS' : size,
        'SPECTRAL_RESOLUTION' : 4000,
        'WAVEMIN' : 1.572,
        'WAVECEN' : 1.992,
        'WAVEMAX' : 2.412,
        'BANDWIDTH' : 2.412 - 1.572
    })

    modes_slicer = make_empty_table()
    for row in rows:
        modes_slicer.add_row(row)

    modes_all = astropy.table.vstack((modes_imager, modes_lenslet, modes_slicer))

    return modes_all