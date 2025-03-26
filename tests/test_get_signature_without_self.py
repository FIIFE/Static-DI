from static_di.get_signature_without_self import get_signature_without_self

def test_get_signature_without_self():
    class TestClass:
        def __init__(self, test_arg: int, test_arg_2: str) -> None: ...
    signature_without_self = get_signature_without_self(TestClass)
    params = list(signature_without_self.parameters.values())
    assert len(params) == 2
    assert params[0].name == "test_arg"
    assert params[0].annotation == int
    assert params[1].name == "test_arg_2"
    assert params[1].annotation == str