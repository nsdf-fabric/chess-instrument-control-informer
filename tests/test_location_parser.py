from chess_instrument_control_informer.locations import parse_location_file


def test_parse_location_file_handles_unicode_minus(tmp_path):
    loc = tmp_path / "loc001.txt"
    loc.write_text("labx,labz\n−47.33,-242.5\n")

    points = parse_location_file(str(loc))
    assert points == [(-47.33, -242.5)]
