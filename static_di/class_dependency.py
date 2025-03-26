from functools import wraps
from typing import Optional, cast
from static_di.resolve_arguments import ResolveArguments
from static_di.interfaces import IClassDependency, IScope

class ClassDependency(IClassDependency):
    def __init__(
        self,
        value,
        *,
        resolve_as = 'singleton',
        root = False,
        config = None,
        resolve_arguments = None,
        add_root_dependency = None,
    ):
        self._value = value
        self._mode = resolve_as
        self._config = config
        self._resolve_arguments = resolve_arguments or ResolveArguments()

        self.scope_to_resolve_dependencies_in: Optional[IScope] = None
        self._scope_locked = False
        self._fixed_instance = None
        if root and add_root_dependency:
            add_root_dependency(self)

    @property
    def value(self):
        return self._value
    
    @property
    def resolve_as(self):
        return self._mode

    def set_resolution_scope(self, scope: IScope, lock_scope: bool = False):
        if self._scope_locked is True:
            return
        self.scope_to_resolve_dependencies_in = scope
        self._scope_locked = lock_scope

    def resolve(self):
        if self._fixed_instance: return self._fixed_instance

        if self.scope_to_resolve_dependencies_in is None:
            raise ValueError("scope_to_resolve_dependencies_in was not set. Nest Dependency within Scope")

        match self._mode:
            case "instances":
                return self._resolve_as_instance()
            case "singleton":
                self._fixed_instance = self._resolve_as_instance()
                return self._fixed_instance
            case "factory":
                self._fixed_instance = self._resolve_as_factory()
                return self._fixed_instance
            
    def _resolve_as_instance(self):
        if "__init__" not in self._value.__dict__: return self._value()
        if "kwarg_key_naming_func" not in self._config: raise ValueError("kwarg_key_naming_func is falsy, check your Dependency(...) or DependencyInjector(...) calls for invalid config")
        return self._resolve_arguments(self._value, cast(IScope, self.scope_to_resolve_dependencies_in), self._config)

    def _resolve_as_factory(self):
        if "__init__" not in self._value.__dict__: return self._value
        @wraps(self._value)
        def wrapper(*args, **kwargs):
            if "kwarg_key_naming_func" not in self._config: raise ValueError("kwarg_key_naming_func is falsy, check your Dependency(...) or DependencyInjector(...) calls for invalid config")
            return self._resolve_arguments(self._value, cast(IScope, self.scope_to_resolve_dependencies_in), self._config, user_args={"args": args, "kwargs": kwargs})
        return wrapper