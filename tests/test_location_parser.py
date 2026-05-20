from chess_instrument_control_informer.locations import parse_location_file


def test_parse_location_file_handles_unicode_minus(tmp_path):
    loc = tmp_path / "loc001.txt"
    loc.write_text("labx,labz\n−47.33,-242.5\n")

    points = parse_location_file(str(loc))
    assert points == [(-47.33, -242.5)]


def test_parse_location_file_handles_comma_header(tmp_path):
    loc = tmp_path / "loc001.txt"
    loc.write_text("labx,labz\n1.0,2.0\n3.0,4.0\n")

    assert parse_location_file(str(loc)) == [(1.0, 2.0), (3.0, 4.0)]


def test_parse_location_file_handles_whitespace_header(tmp_path):
    loc = tmp_path / "loc001.txt"
    loc.write_text("labx labz\n1.0 2.0\n3.0 4.0\n")

    assert parse_location_file(str(loc)) == [(1.0, 2.0), (3.0, 4.0)]


def test_parse_location_file_handles_whitespace_without_header_and_blanks(tmp_path):
    loc = tmp_path / "loc001.txt"
    loc.write_text("\n1.0 2.0\n\n3.0 4.0\n")

    assert parse_location_file(str(loc)) == [(1.0, 2.0), (3.0, 4.0)]
