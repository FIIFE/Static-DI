from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Type, Union, overload

if TYPE_CHECKING:
    from static_di.interfaces import IScope, IResolveArguments, IPartialConfig, IConfig

class IClassHolder(ABC):
    @property
    @abstractmethod
    def value(self)-> Type: ... 

class IValueHolder(ABC):
    @property
    @abstractmethod
    def value(self)-> Any: ... 
    
class IScopeSetter(ABC):
    @abstractmethod
    def set_resolution_scope(self, scope: "IScope", lock_scope: bool = False) -> None: ...

class IModable(ABC):
    @property
    @abstractmethod
    def resolve_as(self) -> Literal["singleton", "instances", "factory"]: ...

class IResolvable(ABC):
    @abstractmethod
    def resolve(self) -> None: ...

class IClassDependency(IResolvable, IClassHolder, IScopeSetter, IModable):
    def __init__(
        self,
        value: Type,
        *,
        resolve_as: Literal["singleton", "instances", "factory"] = ...,
        root: bool = ...,
        config: "IConfig" = ...,
        resolve_arguments: Optional["IResolveArguments"] = ...,
        add_root_dependency: Optional[Callable[["IClassDependency"], None]] = ...
    ): ...

class IValueDependency(IResolvable, IValueHolder):
    def __init__(self, value: Any): ...

class IDependencyFactory(ABC):
    """
    Creates a dependency ready to be passed to scope.

    Args:
        value: value of a dependency to register.
        resolve_as: determines how should dependency be resolved.
            - `singleton` - shares single instance across dependents
            - `instances` - creates new instance for each dependent
            - `factory` - resolves as a factory function that when called instantiates the passed class with dependencies injected
        root: if True marks this dependency as a starting point for resolution process.
        config: a typed dictionary specifying resolution behaviour of this dependency. Omitted props default to config values defined in DependencyInjector. Accepts the following props.
            
            - `aggregate: Set[Any] = { type }`: A set of type annotations that determine which dependencies should be aggregated.
              When a parameter is annotated with one of these types, all matching dependencies will be injected as a list.
              
            - `aggregate_strategy: Literal["self_scope", "full"] = "self_scope"`: Defines the aggregation strategy.
              Use "self_scope" to limit aggregation to the current scope only, or "full" to aggregate from all available scopes.
              
            - `kwarg_key_naming_func: Callable[[str, int], str] = lambda arg_name, index: f"{arg_name}_{index}"`: A function that determines how keyword argument keys
              are named when injecting aggregated dependencies via **kwargs.

    Returns:
        dependency: either `IClassDependency` or `IValueDependency` instance ready to be passed into scope.
    Example:
        value dependency:
        >>> Dependency("sample_string")

        class dependency:
        >>> Dependency(
                SampleClass,
                resolve_as="instances",
                root=True,
                config={
                    "aggregate": {int, str},
                    "aggregate_strategy": "full",
                    "kwarg_key_naming_func": lambda name, index: f"test_{name}_{index}"
                }
            )
    """
    @overload
    def __new__(
        cls,
        value: Type,
        *,
        resolve_as: Literal["singleton", "instances", "factory"] = "singleton",
        root: bool = False,
        config: "IPartialConfig" = ...
    ) -> IClassDependency: ...

    @overload
    def __new__(cls, value: Any) -> IValueDependency: ...
    
    def __new__(cls, value: Any, *args, **kwargs) -> Union[IClassDependency, IValueDependency]: ...