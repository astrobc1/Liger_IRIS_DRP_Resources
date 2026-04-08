from liger_iris_drp_resources.gratings import load_gratings_summary

def test_gratings():

    gratings = load_gratings_summary()

    assert isinstance(gratings, dict)
    assert len(gratings) > 0

    for name, info in gratings.items():
        assert info['wavemin'] > 0
        assert info['wavemax'] > info['wavemin'], f"wavemax <= wavemin for {name}"
        assert info['wavecenter'] > info['wavemin'], f"wavecenter <= wavemin for {name}"
        assert info['wavecenter'] < info['wavemax'], f"wavecenter >= wavemax for {name}"
        assert info['resolution'] > 0
        assert info['groov_density'] > 0
