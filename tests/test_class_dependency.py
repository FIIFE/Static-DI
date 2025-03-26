import inspect
from typing import Type, cast
import pytest
from unittest.mock import MagicMock
from static_di.default_config import default_config
from static_di.class_dependency import ClassDependency
from static_di.resolve_arguments import ResolveArguments

class DummyClass:
    def __init__(self) -> None: ...

def test_init_sets_attributes_correctly():
    dependency = ClassDependency(DummyClass)
    assert dependency._value == DummyClass
    assert dependency._mode == "singleton"
    assert dependency._config == None
    assert isinstance(dependency._resolve_arguments, ResolveArguments) == True
    assert dependency.scope_to_resolve_dependencies_in == None
    assert dependency._scope_locked == False
    assert dependency._fixed_instance == None

def test_add_root_dependency_on_init():
    root_dependencies = []
    dependency = ClassDependency(DummyClass, root=True, add_root_dependency=lambda x: root_dependencies.append(x))
    assert root_dependencies == [dependency]

def test_set_resolution_scope():
    # Initialize dependencies for testing
    dependency = ClassDependency(DummyClass)
    
    # First call: set scope without locking
    scope1 = MagicMock()
    dependency.set_resolution_scope(scope1)
    assert dependency.scope_to_resolve_dependencies_in == scope1
    assert dependency._scope_locked is False
    
    # Second call: set new scope with lock enabled
    scope2 = MagicMock()
    dependency.set_resolution_scope(scope2, lock_scope=True)
    assert dependency.scope_to_resolve_dependencies_in == scope2
    assert dependency._scope_locked is True
    
    # Third call: attempt to change scope again without locking (should be prevented)
    scope3 = MagicMock()
    dependency.set_resolution_scope(scope3)  # Scope is locked and should not update
    assert dependency.scope_to_resolve_dependencies_in == scope2
    assert dependency._scope_locked is True

def test_resolve_without_scope():
    dependency = ClassDependency(DummyClass)
    with pytest.raises(ValueError):
        dependency.resolve()

def test_resolve_without_kwarg_key_naming_func():
    dependency = ClassDependency(DummyClass, config={}) # type: ignore
    mock_scope = MagicMock()
    dependency.set_resolution_scope(mock_scope)
    with pytest.raises(ValueError):
        dependency.resolve()

def test_resolve_as_singleton():
    resolve_arguments_mock = MagicMock()
    class DepValue: ...
    resolve_arguments_mock.side_effect = lambda a, b, c: DepValue()
    dependency = ClassDependency(DummyClass, config={"aggregate": {type}, "aggregate_strategy":"self_scope","kwarg_key_naming_func":lambda x, y: "test"}, resolve_arguments=resolve_arguments_mock)
    mock_scope = MagicMock()
    dependency.set_resolution_scope(mock_scope)
    first_resolve_return_val = dependency.resolve()
    assert dependency._fixed_instance == first_resolve_return_val
    second_resolve_return_val = dependency.resolve()
    assert second_resolve_return_val == first_resolve_return_val
    resolve_arguments_mock.assert_called_once()

def test_resolve_as_instances():
    resolve_arguments_mock = MagicMock()
    class DepValue: ...
    resolve_arguments_mock.side_effect = lambda a, b, c: DepValue()
    dependency = ClassDependency(DummyClass, resolve_as="instances", config={"aggregate": {type}, "aggregate_strategy":"self_scope","kwarg_key_naming_func":lambda x, y: "test"}, resolve_arguments=resolve_arguments_mock)
    mock_scope = MagicMock()
    dependency.set_resolution_scope(mock_scope)
    first_resolve_return_val = dependency.resolve()
    assert dependency._fixed_instance == None
    second_resolve_return_val = dependency.resolve()
    assert second_resolve_return_val != first_resolve_return_val
    assert resolve_arguments_mock.call_count == 2

def test_resolve_as_factory():
    resolve_arguments_mock = MagicMock()
    class DepValue: ...
    resolve_arguments_mock.side_effect = lambda a, b, c, user_args: DepValue()
    dependency = ClassDependency(DummyClass, resolve_as="factory", config={"aggregate": {type}, "aggregate_strategy":"self_scope","kwarg_key_naming_func":lambda x, y: "test"}, resolve_arguments=resolve_arguments_mock)
    mock_scope = MagicMock()
    dependency.set_resolution_scope(mock_scope)
    first_resolve_return_val = cast(Type[DummyClass], dependency.resolve())
    assert isinstance(first_resolve_return_val(), DepValue)
    assert callable(first_resolve_return_val) == True
    assert dependency._fixed_instance == first_resolve_return_val
    second_resolve_return_val = dependency.resolve()
    assert second_resolve_return_val == first_resolve_return_val