from target_mako.dict_proxy import wrap_namespace


def test_access_attribute():
    # given
    record_dict = {
        "checked": True,
        "dimensions": {
            "width": 20,
            "height": 40
        },
        "tags": ["rNEZGFXulwhyahOLnDEKRYAzbvHvkMRLsBSMxMxRRFkVhrvPoTeTgl",
                 "WfCqViSIjILXTiUxHWPMKhYBHHvwjpjGewtvKezMrKXxgHiXavUWmCBDXkOBHNlGDSzvFvsYZgztrpmxDAxIFz",
                 "AWiLOHpyJDWRzSoZLWlFtPxLHwIxSyPDcgHWIQznfmGhPiTZPBXpQinmVWnQpQQDufH", "CFEpSHIrsQRhQArc",
                 "sDxgDwkbCxydjFiUdAKpGUtvSkslNyRXHIfLiOHsCtoAzvKmuhXkUAiaZTDAWyHsLtflCWqouPRsrbDAAIoVgQjN",
                 "VSEUqAEMWVgiJZZqhgKiRTAGzFbSvfnCP", "ThcDIgAItOnp", "jFpmDZckKYJeFmjPSCiWiCKavrOldVdWcyD"],
        "inner": [
            {"key1": "value1"},
            {"key1": "value2"}
        ]
    }
    # when
    record_values = wrap_namespace(record_dict)
    # then
    assert record_values.checked is not None
    assert record_values.checked is True
    assert record_values.dimensions.width is not None
    assert 20 == record_values.dimensions.width
    assert record_values.dimensions.height is not None
    assert 40 == record_values.dimensions.height
    assert record_values.tags[0] is not None
    assert "rNEZGFXulwhyahOLnDEKRYAzbvHvkMRLsBSMxMxRRFkVhrvPoTeTgl" == record_values.tags[0]
    assert record_values.inner[0].key1 is not None
    assert "value1" == record_values.inner[0].key1
    assert record_values.inner[1].key1 is not None
    assert "value2" == record_values.inner[1].key1


def test_access_invalid_attribute():
    # given
    record_dict = {
        "checked": True,
        "dimensions": {
            "width": 20,
            "height": 40
        }
    }
    # when
    record_values = wrap_namespace(record_dict)

    # then
    assert record_values.invalid is not None
    assert str(record_values.invalid) == ""


def test_access_inner_invalid_attribute():
    # given
    record_dict = {
        "checked": True,
        "dimensions": {
            "width": 20,
            "height": 40
        }
    }
    # when
    record_values = wrap_namespace(record_dict)
    # then
    assert record_values.invalid.width is not None
    assert str(record_values.invalid.width) == ""


def test_access_inner_invalid2_attribute():
    # given
    record_dict = {
        "checked": True,
        "inner": [
            None,
            {"key1": "value2"}
        ]
    }
    # when
    record_values = wrap_namespace(record_dict)
    # then
    assert record_values.inner[0].key1 is not None
    assert str(record_values.inner[0].key1) == ""
    assert record_values.inner[1].key1 is not None
    assert "value2" == record_values.inner[1].key1


def test_access_inner_invalid3_attribute():
    # given
    record_dict = {
        "checked": True,
        "dimensions": None,
    }
    # when
    record_values = wrap_namespace(record_dict)
    # then
    assert record_values.dimensions.width is not None
    assert str(record_values.dimensions.width) == ""


def test_access_inner_invalid4_attribute():
    # given
    record_dict = {
        "checked": True,
        "dimensions": None,
        "tags": ["rNEZGFXulwhyahOLnDEKRYAzbvHvkMRLsBSMxMxRRFkVhrvPoTeTgl",
                 None,
                 "AWiLOHpyJDWRzSoZLWlFtPxLHwIxSyPDcgHWIQznfmGhPiTZPBXpQinmVWnQpQQDufH", "CFEpSHIrsQRhQArc",
                 "sDxgDwkbCxydjFiUdAKpGUtvSkslNyRXHIfLiOHsCtoAzvKmuhXkUAiaZTDAWyHsLtflCWqouPRsrbDAAIoVgQjN",
                 "VSEUqAEMWVgiJZZqhgKiRTAGzFbSvfnCP", "ThcDIgAItOnp", "jFpmDZckKYJeFmjPSCiWiCKavrOldVdWcyD"],
    }
    # when
    record_values = wrap_namespace(record_dict)
    # then
    assert record_values.tags[1] is not None
    assert str(record_values.tags[1]) == ""
