from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Type, Union

if TYPE_CHECKING:
    from static_di.interfaces import IClassDependency, IValueDependency

class IScope(ABC):
    """
    Creates a scope for building a hierarchical structure in which dependencies can be registered.

    Args:
        dependencies: a list to register dependencies in.
        dependents: a list of dependencies that should act as dependents within this scope. Useful when a dependency is intended to be used as a regular dependency in one scope and as a dependent in another.
        scopes: a list to put nested scopes in.
    Returns:
        scope: an instance of scope to build hierarchical structure with.
    Example:
        simple structure:
        >>> Scope(
                dependencies=[
                    Dependency(RootDependency, root=True),
                    Dependency("sample_string")
                ]
            )
        
        advenced structure:
        >>> multi_scope_dep = Dependency(MultiScopeDep)
            Scope(
                dependencies=[
                    Dependency(RootDep, root=True),
                    Dependency("sample_string"),
                    multi_scope_dep
                ],
                scopes=[
                    Scope(
                        dependencies=[
                            Dependency("nested_sample_string")
                        ],
                        dependents=[
                            multi_scope_dep,
                        ]
                    )
                ]
            )
    """
    def __init__(
        self,
        *,
        scopes: List["IScope"] = [],
        dependencies: List[Union["IClassDependency", "IValueDependency"]] = [],
        dependents: List["IClassDependency"] = []
    ): ...

    @property
    @abstractmethod
    def categorized_dependencies(self) -> Dict[Type[Any], List[Union["IClassDependency", "IValueDependency"]]]: ...

    @property
    @abstractmethod
    def uncategorized_dependencies(self) -> List[Union["IClassDependency", "IValueDependency"]]: ...

    @property
    @abstractmethod
    def parent_scope(self) -> "IScope": ...

    @parent_scope.setter
    @abstractmethod
    def parent_scope(self, scope: "IScope") -> None: ...

    @abstractmethod
    def categorize_dependencies(self, type: Type[Any], dependencies: List[Union["IClassDependency", "IValueDependency"]]): ...