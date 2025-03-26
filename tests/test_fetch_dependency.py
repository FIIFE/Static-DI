from typing import Any, List, Type
from unittest.mock import MagicMock, PropertyMock
import pytest
from static_di.fetch_dependency import FetchDependency

def fetch_dependency_factory(requested_type, scope: Any = MagicMock(), aggregate = False, aggregate_strategy = "self_scope", index_of_dep_to_fetch = 0):
    return FetchDependency()(requested_type, scope, aggregate, aggregate_strategy, index_of_dep_to_fetch) # type: ignore

def test_with_no_scope():
    class TestType: ...
    dependency = fetch_dependency_factory(TestType, scope=None)
    assert dependency == None

def test_with_no_deps_in_scope():
    class TestType: ...
    scope_mock = MagicMock()
    type(scope_mock).categorized_dependencies = PropertyMock(return_value={})
    type(scope_mock).uncategorized_dependencies = PropertyMock(return_value=[])
    type(scope_mock).parent_scope = PropertyMock(return_value=None)
    dependency = fetch_dependency_factory(TestType, scope_mock)
    assert dependency == None

def test_factory_dep():
    scope_mock = MagicMock()
    type(scope_mock).categorized_dependencies = PropertyMock(return_value={})
    dep_mock = MagicMock()
    class TestBase: ...
    class TestFactoryDep(TestBase): ...
    type(dep_mock).value = PropertyMock(return_value=Type[TestFactoryDep])
    type(dep_mock).resolve = MagicMock(return_value=TestFactoryDep)
    type(scope_mock).uncategorized_dependencies = PropertyMock(return_value=[dep_mock])
    def categorize_dependencies_mock(a, b):
        type(scope_mock).categorized_dependencies = PropertyMock(return_value={Type[TestBase]: [dep_mock]})
    type(scope_mock).categorize_dependencies = MagicMock(side_effect=categorize_dependencies_mock)
    type(scope_mock).parent_scope = PropertyMock(return_value=None)
    dependency = fetch_dependency_factory(Type[TestBase], scope_mock)
    assert dependency == TestFactoryDep

def test_singleton_and_instance_dep():
    scope_mock = MagicMock()
    type(scope_mock).categorized_dependencies = PropertyMock(return_value={})
    dep_mock = MagicMock()
    class TestBase: ...
    class TestDep(TestBase): ...
    type(dep_mock).value = PropertyMock(return_value=TestDep)
    resolved_dep = TestDep()
    type(dep_mock).resolve = MagicMock(return_value=resolved_dep)
    type(scope_mock).uncategorized_dependencies = PropertyMock(return_value=[dep_mock])
    def categorize_dependencies_mock(a, b):
        type(scope_mock).categorized_dependencies = PropertyMock(return_value={TestBase: [dep_mock]})
    type(scope_mock).categorize_dependencies = MagicMock(side_effect=categorize_dependencies_mock)
    type(scope_mock).parent_scope = PropertyMock(return_value=None)
    dependency = fetch_dependency_factory(TestBase, scope_mock)
    assert dependency == resolved_dep

def test_int_dep():
    scope_mock = MagicMock()
    type(scope_mock).categorized_dependencies = PropertyMock(return_value={})
    dep_mock = MagicMock()
    type(dep_mock).value = PropertyMock(return_value=5)
    type(dep_mock).resolve = MagicMock(return_value=5)
    type(scope_mock).uncategorized_dependencies = PropertyMock(return_value=[dep_mock])
    def categorize_dependencies_mock(a, b):
        type(scope_mock).categorized_dependencies = PropertyMock(return_value={int: [dep_mock]})
    type(scope_mock).categorize_dependencies = MagicMock(side_effect=categorize_dependencies_mock)
    type(scope_mock).parent_scope = PropertyMock(return_value=None)
    dependency = fetch_dependency_factory(int, scope_mock)
    assert dependency == 5

def test_nested_dep():
    parent_scope_mock = MagicMock()
    child_scope_mock = MagicMock()
    type(child_scope_mock).categorized_dependencies = PropertyMock(return_value={})
    type(child_scope_mock).uncategorized_dependencies = PropertyMock(return_value=[])
    type(child_scope_mock).parent_scope = PropertyMock(return_value=parent_scope_mock)
    type(parent_scope_mock).categorized_dependencies = PropertyMock(return_value={})
    dep_mock = MagicMock()
    type(dep_mock).value = PropertyMock(return_value=5)
    type(dep_mock).resolve = MagicMock(return_value=5)
    type(parent_scope_mock).uncategorized_dependencies = PropertyMock(return_value=[dep_mock])
    def categorize_dependencies_mock(a, b):
        type(parent_scope_mock).categorized_dependencies = PropertyMock(return_value={int: [dep_mock]})
    type(parent_scope_mock).categorize_dependencies = MagicMock(side_effect=categorize_dependencies_mock)
    type(parent_scope_mock).parent_scope = PropertyMock(return_value=None)
    dependency = fetch_dependency_factory(int, child_scope_mock)
    assert dependency == 5

def test_self_scope_aggregate_dep():
    scope_mock = MagicMock()
    dep_mock = MagicMock()
    type(dep_mock).resolve = MagicMock(return_value=5)
    dep_mock_2 = MagicMock()
    type(dep_mock_2).resolve = MagicMock(return_value=4)
    type(scope_mock).categorized_dependencies = PropertyMock(return_value={int: [dep_mock, dep_mock_2]})
    type(scope_mock).parent_scope = PropertyMock(return_value=None)
    dependency = fetch_dependency_factory(int, scope_mock, True)
    assert dependency == [5, 4]

def test_full_aggregate_dep():
    parent_scope_mock = MagicMock()
    dep_mock = MagicMock()
    type(dep_mock).resolve = MagicMock(return_value=5)
    type(parent_scope_mock).categorized_dependencies = PropertyMock(return_value={int: [dep_mock]})
    child_scope_mock = MagicMock()
    dep_mock_2 = MagicMock()
    type(dep_mock_2).resolve = MagicMock(return_value=4)
    type(child_scope_mock).categorized_dependencies = PropertyMock(return_value={int: [dep_mock_2]})
    type(child_scope_mock).parent_scope = PropertyMock(return_value=parent_scope_mock)
    type(parent_scope_mock).parent_scope = PropertyMock(return_value=None)
    dependency = fetch_dependency_factory(int, child_scope_mock, True, "full")
    assert dependency == [4, 5]

def test_index_out_of_range():
    scope_mock = MagicMock()
    dep_mock = MagicMock()
    type(dep_mock).resolve = MagicMock(return_value=5)
    type(scope_mock).parent_scope = PropertyMock(return_value=None)
    type(scope_mock).categorized_dependencies = PropertyMock(return_value={int: [dep_mock]})
    with pytest.raises(IndexError, match="^Trying to access int dependency at index 1 but the number of int dependencies is lower than 2. Make sure there are at least 2 int dependencies in scope$"):
        fetch_dependency_factory(int, scope_mock, index_of_dep_to_fetch=1)