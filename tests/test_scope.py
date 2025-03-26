from typing import Any, List, Type, Union, cast
from unittest.mock import MagicMock
from static_di import Scope
from static_di.interfaces import IClassDependency, IScopeSetter, IValueDependency, IDependencyFactory

def test_init_without_parameters():
    scope = Scope()
    assert not scope._parent_scope
    assert not scope._categorized_dependencies
    assert not scope._uncategorized_dependencies

def test_set_parent_scope():
    child = Scope()
    parent = Scope(scopes=[child])
    assert child.parent_scope == parent

def test_add_dependencies():
    class DepClass:
        def __init__(self, value: Any) -> None: ...
            
    class MockClass: ...
    MockClassImpl = cast(Type[IDependencyFactory], DepClass)

    mock_dependencies = [MockClassImpl(MockClass), MockClassImpl("test"), MockClassImpl(MockClass)]

    scope = Scope(dependencies=mock_dependencies)
    assert scope._uncategorized_dependencies == mock_dependencies

def test_set_resolution_scope_by_dependencies():
    set_resolution_scope_prop = MagicMock()
    class MockClassDep(IScopeSetter):
        set_resolution_scope = set_resolution_scope_prop
    scope = Scope(dependencies=[cast(IClassDependency, MockClassDep())])
    set_resolution_scope_prop.assert_called_with(scope)

def test_set_resolution_scope_by_dependents():
    set_resolution_scope_prop = MagicMock()
    class MockClassDep(IScopeSetter):
        set_resolution_scope = set_resolution_scope_prop
    scope = Scope(dependents=[cast(IClassDependency, MockClassDep())])
    set_resolution_scope_prop.assert_called_with(scope, True)

def test_categorize_dependencies():
    scope = Scope()
    mock_dependencies = [1, 2, 3]
    scope.categorize_dependencies(str, cast(List[Union[IClassDependency, IValueDependency]], mock_dependencies))
    
    assert scope.categorized_dependencies == {str: [1, 2, 3]}