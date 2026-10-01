from importlib import resources


def test_py_typed_is_shipped():
    # downstream type-checkers only honor annotations if the marker
    # travels with the installed package (PEP 561)
    assert (resources.files("alfalak") / "py.typed").is_file()
