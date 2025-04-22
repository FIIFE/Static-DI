from abc import ABC
import inspect
from typing import TYPE_CHECKING, Callable, Tuple, Type
from static_di.default_config import default_config

if TYPE_CHECKING:
    from static_di.interfaces import IDependencyFactory, IScope, IPartialConfig, IClassDependency, IValueDependency

class IDependencyInjector(ABC):
    def __new__(
        cls,
        config: "IPartialConfig" = ...,
        get_signature_without_self: Callable[[Type], inspect.Signature] = ...,
        scope: Type["IScope"] = ...,
        class_dependency: Type["IClassDependency"] = ...,
        value_dependency: Type["IValueDependency"] = ...
    ) -> Tuple[Type["IScope"], Type["IDependencyFactory"], Callable[[], None]]: ...

class IDependencyInjectorFactory(ABC):
    """
    Initializes the DependencyInjector with optional configuration.

    Args:
        config: a typed dictionary specifying dependency resolution behaviour accepting the following props.
            
            - `aggregate: Set[Any] = { type }`: A set of type annotations that determine which dependencies should be aggregated.
              When a parameter is annotated with one of these types, all matching dependencies will be injected as a list.
              
            - `aggregate_strategy: Literal["self_scope", "full"] = "self_scope"`: Defines the aggregation strategy.
              Use "self_scope" to limit aggregation to the current scope only, or "full" to aggregate from all available scopes.
              
            - `kwarg_key_naming_func: Callable[[str, int], str] = lambda arg_name, index: f"{arg_name}_{index}"`: A function that determines how keyword argument keys
              are named when injecting aggregated dependencies via **kwargs.

    Returns:
        tuple:
            - `Scope: Type[IScope]`: A class used to construct hierarchical scopes to register dependencies in.
            - `Dependency: Type[IDependencyFactory]`: A class used to register dependencies.
            - `resolve: Callable[[], None]`: A function that triggers resolution of all root dependencies, starting the injection process.
    Example:
        without arguments:
        >>> Scope, Dependency, resolve = DependencyInjector()

        with arguments:
        >>> Scope, Dependency, resolve = DependencyInjector({
            "aggregate": {type, int, dict},
            "aggregate_strategy": "full",
            "kwarg_key_naming_func": lambda name, index: f"test_{name}_{index}"
            })
    """
    def __new__(cls, config: "IPartialConfig" = default_config) -> tuple[Type["IScope"], Type["IDependencyFactory"], Callable[[], None]]: ... # type: ignore