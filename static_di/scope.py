from __future__ import annotations
from typing import Any, Dict, List, Optional, Type, Union
from static_di.interfaces import IScope, IClassDependency, IValueDependency, IScopeSetter

class Scope(IScope):
    def __init__(
        self,
        *,
        scopes = [],
        dependencies = [],
        dependents = []
    ):
        self._parent_scope: Optional[IScope] = None
        self._categorized_dependencies: Dict[Type[Any], List[Union[IClassDependency, IValueDependency]]] = {}
        self._uncategorized_dependencies: List[Union[IClassDependency, IValueDependency]] = dependencies

        for scope in scopes:
            scope.parent_scope = self

        for dependency in dependencies:
            if isinstance(dependency, IScopeSetter):
                dependency.set_resolution_scope(self)
    
        for dependent in dependents:
            dependent.set_resolution_scope(self, True)

    def categorize_dependencies(self, type: Type[Any], dependencies: List[Union[IClassDependency, IValueDependency]]):
        self.categorized_dependencies[type] = dependencies

    @property
    def categorized_dependencies(self):
        return self._categorized_dependencies
    
    @property
    def uncategorized_dependencies(self):
        return self._uncategorized_dependencies

    @property
    def parent_scope(self):
        return self._parent_scope

    @parent_scope.setter
    def parent_scope(self, scope: IScope):
        self._parent_scope = scope