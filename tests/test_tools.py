from velmo.tools import available_tools


def test_lookup_order_is_exposed():
    assert "lookup_order" in available_tools()


def test_track_delivery_is_exposed():
    assert "track_delivery" in available_tools()


def test_open_after_sales_is_exposed():
    assert "open_after_sales" in available_tools()
