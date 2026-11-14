from pdf_generator.pdf_generator import calculate_layout, get_page_size

import pytest


def test_a4_page_size_portrait():
    width, height = get_page_size("A4", "portrait", (1000, 1500))
    assert height > width


def test_auto_orientation_follows_image():
    width, height = get_page_size("A4", "auto", (1600, 900))
    assert width > height


def test_contain_fits_inside_available_area():
    x, y, width, height = calculate_layout(
        image_size=(1600, 900),
        page_size=(600, 800),
        fit="contain",
        margin=20,
    )
    assert width <= 560
    assert height <= 760
    assert x >= 20
    assert y >= 20


def test_stretch_uses_available_area():
    result = calculate_layout(
        image_size=(100, 200),
        page_size=(600, 800),
        fit="stretch",
        margin=10,
    )
    assert result == (10.0, 10.0, 580.0, 780.0)


def test_invalid_margin_rejected():
    with pytest.raises(ValueError):
        calculate_layout((100, 100), (100, 100), "contain", margin=50)
