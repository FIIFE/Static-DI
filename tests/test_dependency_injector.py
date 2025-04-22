import inspect
from typing import Any, Callable, ForwardRef, Type, cast
from unittest.mock import MagicMock
import pytest
from static_di.default_config import default_config
from static_di.class_dependency import ClassDependency
from static_di.dependency_injector import DependencyInjector
from static_di.interfaces import IPartialConfig, IConfig, IDependencyFactory
from static_di.scope import Scope
from static_di.value_dependency import ValueDependency

params = [
        inspect.Parameter("value", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Type),
        inspect.Parameter("root", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=False),
        inspect.Parameter("config", inspect.Parameter.KEYWORD_ONLY, annotation=IConfig, default=None),
        inspect.Parameter("add_root_dependency", inspect.Parameter.KEYWORD_ONLY, annotation=Callable[[ForwardRef("ClassDependency")], type(None)]),
]
get_signature_without_self_mock = MagicMock()
get_signature_without_self_mock.return_value = inspect.Signature(params)

def dependency_injector_with_injected_mocks(config: IPartialConfig = {'aggregate': {type},'aggregate_strategy': "self_scope", 'kwarg_key_naming_func': lambda x, y: "test"}, get_signature_without_self: Any = get_signature_without_self_mock, scope: Any=MagicMock(), class_dependency: Any=MagicMock(), value_dependency: Any=MagicMock()):
    return DependencyInjector(config, get_signature_without_self, cast(type[Scope], scope), cast(type[ClassDependency], class_dependency), cast(type[ValueDependency], value_dependency))

def test_resolve_with_no_root_dep():
    scope, dependency, resolve = dependency_injector_with_injected_mocks()
    with pytest.raises(ValueError):
        resolve()
class DependencyMock:
    def __init__(
        self,
        value: Type,
        *,
        root: bool = False,
        config: IConfig,
        add_root_dependency: Callable[["ClassDependency"], None],
    ):
        self._config = config
        self.add_root_dependency = add_root_dependency
        self.was_resolve_called = False

        if root:
            self.add_root_dependency(cast(ClassDependency, self))

    def resolve(self):
        self.was_resolve_called = True

class MockClass: ...

def test_add_root_class_dep_and_resolve():
    scope, dependency, resolve = dependency_injector_with_injected_mocks(class_dependency=DependencyMock)
    dependency_instance = cast(type[ClassDependency], dependency)(MockClass, root=True)
    resolve()
    assert cast(DependencyMock, dependency_instance).was_resolve_called == True

def test_dependency_overriding():
    scope, dependency, resolve = dependency_injector_with_injected_mocks(class_dependency=DependencyMock)

    kwarg_key_naming_func_mock = lambda x, y: "overriden"
    overriden_config: IPartialConfig = {"kwarg_key_naming_func": kwarg_key_naming_func_mock, "aggregate_strategy":"full"}
    dependency_instance = cast(type[IDependencyFactory], dependency)(MockClass, config=overriden_config)
    assert cast(DependencyMock, dependency_instance)._config["aggregate_strategy"] == "full"
    assert cast(DependencyMock, dependency_instance)._config["kwarg_key_naming_func"] == kwarg_key_naming_func_mock

def test_config_merging():
    class TestClass: ...
    scope, dependency, resolve = dependency_injector_with_injected_mocks({"aggregate": {int}}, class_dependency=DependencyMock)
    dependency_instance = cast(ClassDependency, dependency(TestClass))
    assert dependency_instance._config["aggregate_strategy"] is default_config["aggregate_strategy"]
    assert dependency_instance._config["kwarg_key_naming_func"] is default_config["kwarg_key_naming_func"]
    scope, dependency, resolve = dependency_injector_with_injected_mocks({"kwarg_key_naming_func": lambda x, y: "test"}, class_dependency=DependencyMock)
    dependency_instance = cast(ClassDependency, dependency(TestClass))
    assert dependency_instance._config["aggregate"] is default_config["aggregate"]
    assert dependency_instance._config["aggregate_strategy"] is default_config["aggregate_strategy"]
    scope, dependency, resolve = dependency_injector_with_injected_mocks({}, class_dependency=DependencyMock)
    dependency_instance = cast(ClassDependency, dependency(TestClass))
    assert dependency_instance._config["aggregate"] is default_config["aggregate"]
    assert dependency_instance._config["aggregate_strategy"] is default_config["aggregate_strategy"]
    assert dependency_instance._config["kwarg_key_naming_func"] is default_config["kwarg_key_naming_func"]