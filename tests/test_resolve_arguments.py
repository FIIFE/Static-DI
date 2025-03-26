import inspect
from typing import Callable, List
from unittest.mock import MagicMock, call
import pytest
from static_di.resolve_arguments import ResolveArguments

def resolve_arguments_factory(cls, scope = MagicMock(), config = {"aggregate": {type}, "aggregate_strategy": "self_scope", "kwarg_key_naming_func": lambda name, index: f"{name}_{index}"}, fetch_dependency = MagicMock(), get_signature_without_self = MagicMock(), user_args = {}):
    return ResolveArguments()(cls, scope, config, fetch_dependency, get_signature_without_self, user_args)

def test_class_with_no_args():
    class TestClass:
        def __init__(self) -> None: ...

    instance_with_args_resolved = resolve_arguments_factory(TestClass)

    assert isinstance(instance_with_args_resolved, TestClass)

def test_class_with_user_provided_args():
    class TestClass:
        def __init__(self, pos_only_string: str, /, number: int, string: str, *args: int, kwarg_int: int, **kwargs: str ) -> None:
            self.pos_only_string = pos_only_string
            self.number = number
            self.string = string
            self.args = args
            self.kwarg_int = kwarg_int
            self.kwargs = kwargs

    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("pos_only_string", inspect._ParameterKind.POSITIONAL_ONLY, annotation=str),
        inspect.Parameter("number", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=int),
        inspect.Parameter("string", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=str),
        inspect.Parameter("args", inspect._ParameterKind.VAR_POSITIONAL, annotation=int),
        inspect.Parameter("kwarg_int", inspect._ParameterKind.KEYWORD_ONLY, annotation=int),
        inspect.Parameter("kwargs", inspect._ParameterKind.VAR_KEYWORD, annotation=str)
    ])

    fetch_dependency_mock = MagicMock()
    instance_with_args_resolved = resolve_arguments_factory(TestClass, get_signature_without_self=get_signature_without_self_mock, user_args={"args": ("pos_only_string", 5, "test_string", 7), "kwargs": {"kwarg_int": 6, "custom_kwarg": "test"}}, fetch_dependency=fetch_dependency_mock)

    fetch_dependency_mock.assert_not_called()
    assert isinstance(instance_with_args_resolved, TestClass)
    assert instance_with_args_resolved.pos_only_string == "pos_only_string"
    assert instance_with_args_resolved.number == 5
    assert instance_with_args_resolved.string == "test_string"
    assert instance_with_args_resolved.args == (7,)
    assert instance_with_args_resolved.kwarg_int == 6
    assert instance_with_args_resolved.kwargs == {"custom_kwarg": "test"}

def test_class_with_arg_without_type():
    class TestClass:
        def __init__(self, arg) -> None: ...
    
    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("arg", inspect._ParameterKind.POSITIONAL_OR_KEYWORD),
    ])

    with pytest.raises(ValueError, match="^Argument 'arg' of 'TestClass' was not provided by user, has no annotation and has no default value$"):
        resolve_arguments_factory(TestClass, get_signature_without_self=get_signature_without_self_mock)

def test_class_with_arg_without_type_with_default():
    class TestClass:
        def __init__(self, arg = 5) -> None:
            self.arg = arg
    
    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("arg", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, default=5),
    ])

    fetch_dependency_mock = MagicMock()

    test_class_instance = resolve_arguments_factory(TestClass, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock)

    fetch_dependency_mock.assert_not_called()
    assert test_class_instance.arg == 5

def test_class_with_typed_arg_and_no_dep_found():
    class TestDependency: ...
    class TestClass:
        def __init__(self, arg: TestDependency) -> None: ...
    
    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("arg", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=TestDependency),
    ])

    fetch_dependency_mock = MagicMock()
    fetch_dependency_mock.side_effect = lambda a, b, c, d, e: None

    with pytest.raises(ValueError, match="^Argument 'arg' of 'TestClass' was not provided by user, has no matching dependency and has no default value$"):
        resolve_arguments_factory(TestClass, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock)

def test_class_with_typed_arg_and_dep_found():
    class TestDependency: ...
    class TestClass:
        def __init__(self, arg: TestDependency) -> None:
            self.arg = arg
    
    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("arg", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=TestDependency),
    ])

    arg_instance = TestDependency()
    fetch_dependency_mock = MagicMock()
    fetch_dependency_mock.side_effect = [arg_instance]

    dep_with_resolved_args = resolve_arguments_factory(TestClass, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock)

    assert dep_with_resolved_args.arg == arg_instance

def test_class_with_var_args():
    class VarPosArgDep: ...
    class VarKwargDep: ...
    class TestClass:
        def __init__(self, *args: VarPosArgDep, **kwargs: VarKwargDep) -> None:
            self.args = args
            self.kwargs = kwargs

    fetch_dependency_mock = MagicMock()
    resolved_value = VarPosArgDep()
    resolved_value_2 = VarKwargDep()

    fetch_dependency_mock.side_effect = [[resolved_value], [resolved_value_2]]

    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("args", inspect._ParameterKind.VAR_POSITIONAL, annotation=VarPosArgDep),
        inspect.Parameter("kwargs", inspect._ParameterKind.VAR_KEYWORD, annotation=VarKwargDep),
    ])

    test_class_instance = resolve_arguments_factory(TestClass, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock)

    assert test_class_instance.args == (resolved_value,)
    assert test_class_instance.kwargs == {"kwargs_0": resolved_value_2}

def test_class_with_list_of_builtins_or_callables():
    class TestClass:
        def __init__(self, int_list_dep: List[int], func_list: List[Callable]) -> None: ...

    scope_mock = MagicMock()

    fetch_dependency_mock = MagicMock()
    func_list = [lambda: None, lambda: 1]
    fetch_dependency_mock.side_effect = [[1, 2, 3, 4], func_list]

    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("int_list_dep", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=List[int]),
        inspect.Parameter("func_list", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=List[Callable]),
    ])

    resolve_arguments_factory(TestClass, scope_mock, config={"aggregate": {type}, "aggregate_strategy": "self_scope", "kwarg_key_naming_func": lambda a, b: "test"}, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock)

    assert fetch_dependency_mock.call_args_list[0] == call(List[int], scope_mock, False, "self_scope", 0)
    assert fetch_dependency_mock.call_args_list[1] == call(List[Callable], scope_mock, False, "self_scope", 0)

    fetch_dependency_mock_2 = MagicMock()
    fetch_dependency_mock_2.side_effect = [[1, 2, 3, 4], func_list]

    resolve_arguments_factory(TestClass, scope_mock, config={"aggregate": {int, Callable}, "aggregate_strategy": "full", "kwarg_key_naming_func": lambda a, b: "test"}, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock_2)

    assert fetch_dependency_mock_2.call_args_list[0] == call(int, scope_mock, True, "full", 0)
    assert fetch_dependency_mock_2.call_args_list[1] == call(Callable, scope_mock, True, "full", 0)

def test_class_with_list_of_class_instances():

    class TestClassListItem: ...
    class TestClass:
        def __init__(self, class_list: List[TestClassListItem]) -> None: ...

    scope_mock = MagicMock()

    fetch_dependency_mock = MagicMock()
    fetch_dependency_mock.side_effect = [TestClassListItem(), TestClassListItem()]

    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("class_list", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=List[TestClassListItem]),
    ])

    resolve_arguments_factory(TestClass, scope_mock, config={"aggregate": set(), "aggregate_strategy": "self_scope", "kwarg_key_naming_func": lambda a, b: "test"}, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock)

    fetch_dependency_mock.assert_called_with(List[TestClassListItem], scope_mock, False, "self_scope", 0)

    fetch_dependency_mock_2 = MagicMock()
    fetch_dependency_mock_2.side_effect = [TestClassListItem(), TestClassListItem()]

    resolve_arguments_factory(TestClass, scope_mock, config={"aggregate": {type}, "aggregate_strategy": "full", "kwarg_key_naming_func": lambda a, b: "test"}, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock_2)

    fetch_dependency_mock_2.assert_called_with(TestClassListItem, scope_mock, True, "full", 0)

def test_type_count_increment():
    class TestClass:
        def __init__(self, number1: int, number2: int) -> None: ...

    scope_mock = MagicMock()

    fetch_dependency_mock = MagicMock()
    fetch_dependency_mock.side_effect = [1, 2]

    get_signature_without_self_mock = MagicMock()
    get_signature_without_self_mock.side_effect = lambda cls: inspect.Signature([
        inspect.Parameter("number1", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=int),
        inspect.Parameter("number2", inspect._ParameterKind.POSITIONAL_OR_KEYWORD, annotation=int),
    ])

    resolve_arguments_factory(TestClass, scope_mock, config={"aggregate": set(), "aggregate_strategy": "self_scope", "kwarg_key_naming_func": lambda a, b: "test"}, get_signature_without_self=get_signature_without_self_mock, fetch_dependency=fetch_dependency_mock)

    assert fetch_dependency_mock.call_args_list[0] == call(int, scope_mock, False, "self_scope", 0)
    assert fetch_dependency_mock.call_args_list[1] == call(int, scope_mock, False, "self_scope", 1)