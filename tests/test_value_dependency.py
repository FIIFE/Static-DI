from static_di.value_dependency import ValueDependency

def test_init_sets_attributes_correctly():
    dependency = ValueDependency("test")
    assert dependency.value == "test"

def test_resolve():
    dependency = ValueDependency("test")
    assert dependency.resolve() == "test"