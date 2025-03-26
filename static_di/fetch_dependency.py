from typing import Any, List, Optional, get_args, get_origin
from typeguard import CollectionCheckStrategy, check_type
from static_di.interfaces import IFetchDependency, IClassDependency, IValueDependency

class FetchDependency(IFetchDependency):
    def __call__(self, requested_type, scope, aggregate, aggregate_strategy, index_of_dep_to_fetch = 0):
        dependency_value: Optional[List[Any]] = None

        current_scope = scope
        while current_scope is not None:
            if requested_type not in current_scope.categorized_dependencies:
                matching_deps = []
                for dep in current_scope.uncategorized_dependencies:
                    extracted_class = self.extract_nested_class(requested_type)
                    if extracted_class and isinstance(dep, IClassDependency) and dep.resolve_as == "factory":
                        if issubclass(dep.value, extracted_class):
                            matching_deps.append(dep)
                    elif isinstance(requested_type, type) and isinstance(dep, IClassDependency) and dep.resolve_as in {"singleton", "instances"}:
                        if issubclass(dep.value, requested_type):
                            matching_deps.append(dep)
                    elif isinstance(dep, IValueDependency):
                        try:
                            check_type(dep.value, requested_type, collection_check_strategy=CollectionCheckStrategy.ALL_ITEMS)
                            matching_deps.append(dep)
                        except: ...
                current_scope.categorize_dependencies(requested_type, matching_deps)

            if aggregate:
                if requested_type in current_scope.categorized_dependencies:
                    for dep in current_scope.categorized_dependencies[requested_type]:
                        if not dependency_value:
                            dependency_value =  [dep.resolve()]
                        else:
                            dependency_value.append(dep.resolve())
                if aggregate_strategy == "self_scope":
                    break
            else:
                if requested_type in current_scope.categorized_dependencies and current_scope.categorized_dependencies[requested_type]:
                    matching_dependencies = current_scope.categorized_dependencies[requested_type]
                    if index_of_dep_to_fetch >= len(matching_dependencies):
                        raise IndexError(f"Trying to access {requested_type.__name__} dependency at index {index_of_dep_to_fetch} but the number of {requested_type.__name__} dependencies is lower than {index_of_dep_to_fetch + 1}. Make sure there are at least {index_of_dep_to_fetch + 1} {requested_type.__name__} dependencies in scope")
                    dependency_object = matching_dependencies[index_of_dep_to_fetch]
                    return dependency_object.resolve()
            
            current_scope = current_scope.parent_scope

        return dependency_value
    
    def extract_nested_class(self, tp: Any) -> type | None:
        origin = get_origin(tp)
        args = get_args(tp)

        if origin is type and args and isinstance(args[0], type):
            return args[0]

        return None