from abc import ABC
from typing import Callable, Dict, List, Set, Tuple, Type
from static_di import DependencyInjector

def test_one_dep():
    Scope, Dependency, resolve = DependencyInjector()

    class_initiated = False
    class TestClass:
        def __init__(self) -> None:
            nonlocal class_initiated
            class_initiated = True
    
    Scope(dependencies=[Dependency(TestClass, root=True)])
    resolve()
    assert class_initiated == True

def test_singleton_dep():
    class TestSingleton:
        def __init__(self) -> None:
            ...

    dependency_of_first_class = None
    class TestDependent:
        def __init__(self, test: TestSingleton) -> None:
            nonlocal dependency_of_first_class
            dependency_of_first_class = test
    
    dependency_of_second_class = None
    class TestDependent2:
        def __init__(self, test: TestSingleton) -> None:
            nonlocal dependency_of_second_class
            dependency_of_second_class = test

    class TestRootDependency:
        def __init__(self, test: TestDependent, test2: TestDependent2) -> None: ...

    Scope, Dependency, resolve = DependencyInjector()

    Scope(
        dependencies=[
            Dependency(TestRootDependency, root=True),
            Dependency(TestSingleton),
            Dependency(TestDependent),
            Dependency(TestDependent2)
        ]
    )

    resolve()

    assert dependency_of_first_class is dependency_of_second_class

def test_instances_dep():
    class TestFactoryDep:
        def __init__(self) -> None:
            ...

    dependency_of_first_class = None
    class TestDependent:
        def __init__(self, test: TestFactoryDep) -> None:
            nonlocal dependency_of_first_class
            dependency_of_first_class = test
    
    dependency_of_second_class = None
    class TestDependent2:
        def __init__(self, test: TestFactoryDep) -> None:
            nonlocal dependency_of_second_class
            dependency_of_second_class = test

    class TestRootDependency:
        def __init__(self, test: TestDependent, test2: TestDependent2) -> None: ...

    Scope, Dependency, resolve = DependencyInjector()
    
    Scope(
        dependencies=[
            Dependency(TestRootDependency, root=True),
            Dependency(TestFactoryDep, resolve_as="instances"),
            Dependency(TestDependent),
            Dependency(TestDependent2)
        ]
    )

    resolve()

    assert dependency_of_first_class is not dependency_of_second_class

def test_factory_dep():
    class_dep_instantiated = False
    class TestClassDep:
        def __init__(self) -> None:
            nonlocal class_dep_instantiated
            class_dep_instantiated = True

    class TestClassDepWithoutInit: ...

    class_dep_without_init_instance = None
    class TestRootDep:
        def __init__(self, class_dep: Type[TestClassDep], class_dep_without_init: Type[TestClassDepWithoutInit]) -> None:
            class_dep()
            nonlocal class_dep_without_init_instance
            class_dep_without_init_instance = class_dep_without_init()

    Scope, Dependency, resolve = DependencyInjector()
    
    Scope(
        dependencies=[
            Dependency(TestRootDep, root=True),
            Dependency(TestClassDep),
            Dependency(TestClassDep, resolve_as="factory"),
            Dependency(TestClassDepWithoutInit, resolve_as="factory"),
        ]
    )

    resolve()

    assert class_dep_instantiated is True
    assert isinstance(class_dep_without_init_instance, TestClassDepWithoutInit) is True

def test_standalone_types():
    injected_values = []

    class RootDep:
        def __init__(
            self,
            int_dep: int,
            str_dep: str,
            dict_dep: dict,
            tuple_dep: tuple,
            set_dep: set,
            list_dep: list,
            callable_dep: Callable,
        ) -> None:
            nonlocal injected_values
            injected_values = [
                int_dep,
                str_dep,
                dict_dep,
                tuple_dep,
                set_dep,
                list_dep,
                callable_dep,
            ]

    Scope, Dependency, resolve = DependencyInjector()

    dummy_callable = lambda x: x * 2

    Scope(
        dependencies=[
            Dependency(RootDep, root=True),
            Dependency(42),
            Dependency("hello"),
            Dependency({"key": "value"}),
            Dependency((1, 2, 3)),
            Dependency({1, 2, 3}),
            Dependency([1, 2, 3]),
            Dependency(dummy_callable),
        ]
    )

    resolve()

    assert injected_values[0] == 42
    assert injected_values[1] == "hello"
    assert injected_values[2] == {"key": "value"}
    assert injected_values[3] == (1, 2, 3)
    assert injected_values[4] == {1, 2, 3}
    assert injected_values[5] == [1, 2, 3]
    assert injected_values[6] is dummy_callable

def test_list_dep():
    injected_lists = []
    class RootDep:
        def __init__(
            self,
            int_list_dep: List[int],
            str_list_dep: List[str],
            list_list_dep: List[List],
            dict_list_dep: List[Dict],
            tuple_list_dep: List[Tuple],
            set_list_dep: List[Set],
            func_list_dep: List[Callable],
            complex_list_dep: List[Dict[str, Tuple[Set[Callable], ...]]],
        ) -> None:
            nonlocal injected_lists
            injected_lists = [int_list_dep, str_list_dep, list_list_dep, dict_list_dep, tuple_list_dep, set_list_dep, func_list_dep, complex_list_dep]

    Scope, Dependency, resolve = DependencyInjector()

    func_list = [lambda:None, lambda: "test"]
    func_set = {lambda:None, lambda: "test"}

    Scope(
        dependencies=[
            Dependency(RootDep, root=True),
            Dependency(["one", "two", "three"]),
            Dependency([{"a": 4}, {}, {"b": "dsf"}]),
            Dependency([[], []]),
            Dependency(func_list),
            Dependency([(4,), ("dsf",)]),
            Dependency([1, 2, 3]),
            Dependency([{1, 4}, set(), {"test1", "test2"}]),
            Dependency([{"test": (func_set, func_set)}])
        ]
    )

    resolve()

    assert injected_lists[0] == [1, 2, 3]
    assert injected_lists[1] == ["one", "two", "three"]
    assert injected_lists[2] == [[], []]
    assert injected_lists[3] == [{"a": 4}, {}, {"b": "dsf"}]
    assert injected_lists[4] == [(4,), ("dsf",)]
    assert injected_lists[5] == [{1, 4}, set(), {"test1", "test2"}]
    assert injected_lists[6] == func_list
    assert injected_lists[7] == [{"test": (func_set, func_set)}]

def test_dict_dep():
    injected_dicts = []

    class RootDep:
        def __init__(
            self,
            int_dict_dep: Dict[str, int],
            str_dict_dep: Dict[str, str],
            list_dict_dep: Dict[str, List],
            dict_dict_dep: Dict[str, Dict],
            tuple_dict_dep: Dict[str, Tuple],
            set_dict_dep: Dict[str, Set],
            func_dict_dep: Dict[str, Callable],
            complex_dict_dep: Dict[int, List[Tuple[Set[Callable], ...]]],
        ) -> None:
            nonlocal injected_dicts
            injected_dicts = [
                int_dict_dep, str_dict_dep, list_dict_dep, dict_dict_dep,
                tuple_dict_dep, set_dict_dep, func_dict_dep, complex_dict_dep
            ]

    Scope, Dependency, resolve = DependencyInjector()

    func_set = {lambda: None, lambda: "test"}
    lambda_1 = lambda: 1
    lambda_2 = lambda: 2

    Scope(
        dependencies=[
            Dependency(RootDep, root=True),
            Dependency({"a": 1, "b": 2}),
            Dependency({"x": "one", "y": "two"}),
            Dependency({"l1": [], "l2": []}),
            Dependency({"d1": {}, "d2": {"k": "v"}}),
            Dependency({"t1": (1,), "t2": ("a",)}),
            Dependency({"s1": {1}, "s2": {"b"}}),
            Dependency({"f1": lambda_1, "f2": lambda_2}),
            Dependency({5: [(func_set, func_set)]})
        ]
    )

    resolve()

    assert injected_dicts[0] == {"a": 1, "b": 2}
    assert injected_dicts[1] == {"x": "one", "y": "two"}
    assert injected_dicts[2] == {"l1": [], "l2": []}
    assert injected_dicts[3] == {"d1": {}, "d2": {"k": "v"}}
    assert injected_dicts[4] == {"t1": (1,), "t2": ("a",)}
    assert injected_dicts[5] == {"s1": {1}, "s2": {"b"}}
    assert injected_dicts[6] == {"f1": lambda_1, "f2": lambda_2}
    assert injected_dicts[7] == {5: [(func_set, func_set)]}

def test_tuple_dep():
    injected_tuples = []

    class RootDep:
        def __init__(
            self,
            int_tuple_dep: Tuple[int, ...],
            str_tuple_dep: Tuple[str, ...],
            list_tuple_dep: Tuple[List, ...],
            dict_tuple_dep: Tuple[Dict, ...],
            tuple_tuple_dep: Tuple[Tuple, ...],
            set_tuple_dep: Tuple[Set, ...],
            func_tuple_dep: Tuple[Callable, ...],
            complex_tuple_dep: Tuple[Dict[str, List[Set[Callable]]], ...],
        ) -> None:
            nonlocal injected_tuples
            injected_tuples = [
                int_tuple_dep, str_tuple_dep, list_tuple_dep, dict_tuple_dep,
                tuple_tuple_dep, set_tuple_dep, func_tuple_dep, complex_tuple_dep
            ]

    Scope, Dependency, resolve = DependencyInjector()

    func_set = {lambda: None, lambda: "test"}

    Scope(
        dependencies=[
            Dependency(RootDep, root=True),
            Dependency((1, 2, 3)),
            Dependency(("one", "two", "three")),
            Dependency(([], [])),
            Dependency(({"a": 1}, {})),
            Dependency(((4,), ("b",))),
            Dependency(({1}, {"a"})),
            Dependency((lambda: None, lambda: "func")),
            Dependency(({"nested": [func_set, func_set]},))
        ]
    )

    resolve()

    assert injected_tuples[0] == (1, 2, 3)
    assert injected_tuples[1] == ("one", "two", "three")
    assert injected_tuples[2] == ([], [])
    assert injected_tuples[3] == ({"a": 1}, {})
    assert injected_tuples[4] == ((4,), ("b",))
    assert injected_tuples[5] == ({1}, {"a"})
    assert all(callable(f) for f in injected_tuples[6])
    assert injected_tuples[7] == ({"nested": [func_set, func_set]},)

def test_set_dep():
    injected_sets = []

    class RootDep:
        def __init__(
            self,
            int_set_dep: Set[int],
            str_set_dep: Set[str],
            tuple_set_dep: Set[Tuple],
            func_set_dep: Set[Callable],
        ) -> None:
            nonlocal injected_sets
            injected_sets = [
                int_set_dep, str_set_dep, tuple_set_dep, func_set_dep
            ]

    Scope, Dependency, resolve = DependencyInjector()

    func1, func2 = lambda: None, lambda: "yo"

    Scope(
        dependencies=[
            Dependency(RootDep, root=True),
            Dependency({1, 2, 3}),
            Dependency({"one", "two"}),
            Dependency({(1,), ("x",)}),
            Dependency({func1, func2}),
        ]
    )

    resolve()

    assert injected_sets[0] == {1, 2, 3}
    assert injected_sets[1] == {"one", "two"}
    assert injected_sets[2] == {(1,), ("x",)}
    assert func1 in injected_sets[3] and func2 in injected_sets[3]

def test_overriding_factory_injections():
    class OverridableArgsDep:
        def __init__(self, number_dep: int = 0, string_dep: str = "", list_dep: List = []) -> None:
            self.number_dep = number_dep
            self.string_dep = string_dep
            self.list_dep = list_dep

    overriden_args = []
    partially_overriden_args = []
    partially_overriden_with_some_default_args = []
    class RootDep:
        def __init__(self, all_args_injected_dep: Type[OverridableArgsDep], some_args_injected_dep: Type[OverridableArgsDep]) -> None:
            all_args_injected_dep_instance = all_args_injected_dep(5, "overriden", ["overriden list item"])
            nonlocal overriden_args
            overriden_args = [all_args_injected_dep_instance.number_dep, all_args_injected_dep_instance.string_dep, all_args_injected_dep_instance.list_dep]
            all_args_injected_dep_instance_2 = all_args_injected_dep(3, list_dep=["partially overriden"])
            nonlocal partially_overriden_args
            partially_overriden_args = [all_args_injected_dep_instance_2.number_dep, all_args_injected_dep_instance_2.string_dep, all_args_injected_dep_instance_2.list_dep]
            some_args_injected_dep_instance = some_args_injected_dep(string_dep="overriden")
            nonlocal partially_overriden_with_some_default_args
            partially_overriden_with_some_default_args = [some_args_injected_dep_instance.number_dep, some_args_injected_dep_instance.string_dep, some_args_injected_dep_instance.list_dep]

    Scope, Dependency, resolve = DependencyInjector()

    all_args_injected_dep = Dependency(OverridableArgsDep, resolve_as="factory")
    some_args_injected_dep = Dependency(OverridableArgsDep, resolve_as="factory")

    Scope(
        dependencies=[
            Dependency(RootDep, root=True),
            all_args_injected_dep,
            some_args_injected_dep
        ],
        scopes=[
            Scope(
                dependencies=[
                    Dependency(1),
                    Dependency("injected"),
                    Dependency(["injected list item"]),
                ],
                dependents=[
                    all_args_injected_dep
                ]
            ),
            Scope(
                dependencies=[
                    Dependency("injected"),
                    Dependency(["injected list item"]),
                ],
                dependents=[
                    some_args_injected_dep
                ]
            )
        ]
    )

    resolve()

    assert overriden_args[0] == 5
    assert overriden_args[1] == "overriden"
    assert overriden_args[2] == ["overriden list item"]
    assert partially_overriden_args[0] == 3
    assert partially_overriden_args[1] == "injected"
    assert partially_overriden_args[2] == ["partially overriden"]
    assert partially_overriden_with_some_default_args[0] == 0
    assert partially_overriden_with_some_default_args[1] == "overriden"
    assert partially_overriden_with_some_default_args[2] == ["injected list item"]

def test_nested_scopes():
    Scope, Dependency, resolve = DependencyInjector()

    test_dep_instantiated = False

    class TestDep:
        def __init__(self) -> None:
            nonlocal test_dep_instantiated
            test_dep_instantiated = True
    class TestRootDep:
        def __init__(self, test_dep: TestDep) -> None: ...
            
    
    Scope(
        dependencies=[
            Dependency(TestDep)
        ],
        scopes=[
            Scope(
                dependencies=[
                    Dependency(TestRootDep, root=True)
                ]
            )
        ]
    )
    resolve()
    assert test_dep_instantiated == True

def test_requesting_by_base_class():
    Scope, Dependency, resolve = DependencyInjector()

    class TestParentDep(ABC): ...
        
    test_dep_instantiated = False
    class TestChildDep(TestParentDep):
        def __init__(self) -> None:
            nonlocal test_dep_instantiated
            test_dep_instantiated = True
    class TestRootDep:
        def __init__(self, test_dep: TestParentDep) -> None: ...
            
    
    Scope(
        dependencies=[
            Dependency(TestChildDep)
        ],
        scopes=[
            Scope(
                dependencies=[
                    Dependency(TestRootDep, root=True)
                ]
            )
        ]
    )
    resolve()
    assert test_dep_instantiated == True

def test_multi_scope_dep():
    Scope, Dependency, resolve = DependencyInjector()

    test_dep_instantiated = False
    class TestChildDep():
        def __init__(self) -> None:
            nonlocal test_dep_instantiated
            test_dep_instantiated = True
    class TestRootDep:
        def __init__(self, test_dep: TestChildDep) -> None: ...
            
    root_dep = Dependency(TestRootDep, root=True)

    Scope(
        dependencies=[
            root_dep
        ],
        scopes=[
            Scope(
                dependencies=[
                    Dependency(TestChildDep)
                ],
                dependents=[
                    root_dep
                ]
            )
        ]
    )
    resolve()
    assert test_dep_instantiated == True

def test_multiple_args_with_same_type():
    Scope, Dependency, resolve = DependencyInjector()

    class TestDep: ...

    deps = []
    class TestRootDep:
        def __init__(self, test_dep_1: TestDep, test_dep_2: TestDep) -> None:
            nonlocal deps
            deps = [test_dep_1, test_dep_2]

    Scope(
        dependencies=[
            Dependency(TestRootDep, root=True),
            Dependency(TestDep),
            Dependency(TestDep),
        ]
    )
    resolve()

    assert isinstance(deps[0], TestDep) == True
    assert isinstance(deps[1], TestDep) == True
    assert deps[0] is not deps[1]

def test_aggregate_list_deps():
    Scope, Dependency, resolve = DependencyInjector({"aggregate":{type, int, str, tuple, set, dict, list, Callable}})

    class ListItemDep: ...

    aggregated_deps = []
    class TestRootDep:
        def __init__(
                self,
                class_list_dep: List[ListItemDep],
                list_dep: List[int],
                str_list: List[str],
                tuple_list: List[tuple],
                set_list: List[set],
                dict_list: List[dict],
                list_list: List[list],
                callable_list: List[Callable],
            ) -> None:
            nonlocal aggregated_deps
            aggregated_deps = [class_list_dep, list_dep, str_list, tuple_list, set_list, dict_list, list_list, callable_list]

    lambda_1 = lambda: None
    lambda_2 = lambda: 1

    Scope(
        dependencies=[
            Dependency({"test": 4}),
            Dependency({4: "test"}),
            Dependency(TestRootDep, root=True),
            Dependency(1),
            Dependency(("test", 5)),
            Dependency(("test2",)),
            Dependency(["test"]),
            Dependency([5]),
            Dependency(2),
            Dependency(lambda_1),
            Dependency(lambda_2),
            Dependency(ListItemDep),
            Dependency({1, 2}),
            Dependency({"test"}),
            Dependency(ListItemDep),
            Dependency("test1"),
            Dependency("test2"),
        ]
    )
    resolve()

    assert len(aggregated_deps[0]) == 2 and isinstance(aggregated_deps[0][0], ListItemDep) and isinstance(aggregated_deps[0][1], ListItemDep)
    assert aggregated_deps[1] == [1, 2]
    assert aggregated_deps[2] == ["test1", "test2"]
    assert aggregated_deps[3] == [("test", 5), ("test2",)]
    assert aggregated_deps[4] == [{1, 2}, {"test"}]
    assert aggregated_deps[5] == [{"test": 4}, {4: "test"}]
    assert aggregated_deps[6] == [["test"], [5]]
    assert aggregated_deps[7] == [lambda_1, lambda_2]

def test_aggregate_var_positional_deps():
    Scope, Dependency, resolve = DependencyInjector()

    class TestListDep: ...

    deps = []
    class TestRootDep:
        def __init__(self, *list_dep: TestListDep) -> None:
            for dep in list_dep:
                nonlocal deps
                deps.append(dep)

    Scope(
        dependencies=[
            Dependency(TestRootDep, root=True),
            Dependency(TestListDep),
            Dependency(TestListDep),
            Dependency(TestListDep),
        ]
    )
    resolve()

    assert isinstance(deps[0], TestListDep) == True
    assert isinstance(deps[1], TestListDep) == True
    assert isinstance(deps[2], TestListDep) == True

def test_aggregate_var_keyword_deps():
    Scope, Dependency, resolve = DependencyInjector()

    class TestListDep: ...

    deps = {}
    class TestRootDep:
        def __init__(self, **list_dep: TestListDep) -> None:
            nonlocal deps
            deps = list_dep

    Scope(
        dependencies=[
            Dependency(TestRootDep, root=True),
            Dependency(TestListDep),
            Dependency(TestListDep),
            Dependency(TestListDep),
        ]
    )
    resolve()

    assert isinstance(deps["list_dep_0"], TestListDep) == True
    assert isinstance(deps["list_dep_1"], TestListDep) == True
    assert isinstance(deps["list_dep_2"], TestListDep) == True

def test_config():
    Scope, Dependency, resolve = DependencyInjector({"aggregate":{type, int, dict}, "aggregate_strategy": "full", "kwarg_key_naming_func": lambda name, index: f"test_{name}_{index}"})

    class TestListDep: ...

    config_dep = {}

    class TestClassListConfigDep:
        def __init__(self, **list_dep: TestListDep) -> None:
            nonlocal config_dep
            config_dep = list_dep

    overriden_config_dep = {}

    class TestOverridenConfigDep:
        def __init__(self, **list_dep: TestListDep) -> None:
            nonlocal overriden_config_dep
            overriden_config_dep = list_dep

    num_list_result = None
    class TestNumListConfigDep:
        def __init__(self, num_list: List[int]) -> None:
            nonlocal num_list_result
            num_list_result = num_list

    overriden_num_list_result = None
    class TestOverridenNumListConfigDep:
        def __init__(self, num_list: List[int]) -> None:
            nonlocal overriden_num_list_result
            overriden_num_list_result = num_list

    class TestRootDep:
        def __init__(self, class_list_config_dep: TestClassListConfigDep, overriden_config_dep: TestOverridenConfigDep, num_list_config_dep: TestNumListConfigDep, overriden_num_list_config_dep: TestOverridenNumListConfigDep) -> None: ...

    Scope(
        dependencies=[
            Dependency(TestListDep),
            Dependency(2)
        ],
        scopes=[
            Scope(
                dependencies=[
                    Dependency(TestListDep),
                    Dependency(TestClassListConfigDep),
                    Dependency(TestOverridenConfigDep, config={"aggregate_strategy":"self_scope", "kwarg_key_naming_func":lambda name, index: f"overriden_{name}_{index}"}),
                    Dependency(TestRootDep, root=True),
                    Dependency(TestNumListConfigDep),
                    Dependency(1),
                    Dependency([3, 4]),
                    Dependency(TestOverridenNumListConfigDep, config={"aggregate": set()})
                ]
            )
        ]
    )
    resolve()

    assert isinstance(config_dep["test_list_dep_0"], TestListDep) == True
    assert isinstance(config_dep["test_list_dep_1"], TestListDep) == True
    assert len(overriden_config_dep) == 1
    assert isinstance(overriden_config_dep["overriden_list_dep_0"], TestListDep) == True
    assert num_list_result == [1, 2]
    assert overriden_num_list_result == [3, 4]