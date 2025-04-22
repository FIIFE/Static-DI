from typing import Any, Type, cast
from static_di.class_dependency import ClassDependency
from static_di.default_config import default_config
from static_di.get_signature_without_self import get_signature_without_self
from static_di.interfaces import IClassDependency, IDependencyFactory, IValueDependency, IConfig, IDependencyInjectorFactory, IPartialConfig, IDependencyInjector
from static_di.scope import Scope
from static_di.value_dependency import ValueDependency

class DependencyInjector(IDependencyInjector):
    def __new__(cls, config = {}, get_signature_without_self = get_signature_without_self, scope = Scope, class_dependency = ClassDependency, value_dependency = ValueDependency):
        merged_config: IConfig = {**default_config,  **config}
        if 'aggregate_strategy' not in merged_config or 'kwarg_key_naming_func' not in merged_config:
            raise ValueError("Missing required config props")
        root_dependencies = []

        def add_root_dependency(dependency: IClassDependency):
            nonlocal root_dependencies
            root_dependencies.append(dependency)
        
        def resolve():
            if not root_dependencies:
                raise ValueError("No root dependency defined, define root dependency")
            for root_dependency in root_dependencies:
                root_dependency.resolve()
        
        class DependencyFactory(IDependencyFactory):
            def __new__(cls, value: Any, *args, **kwargs) -> Any:
                if isinstance(value, type):
                    dependency = class_dependency
                else:
                    dependency = value_dependency
                # 
                if issubclass(dependency, IValueDependency):
                    return dependency(value)

                user_config = cast(IPartialConfig, kwargs.pop("config", {}))
                dependency_config: IConfig = {**merged_config, **user_config}

                signature = get_signature_without_self(dependency)
                bound_injected_args = signature.bind_partial(add_root_dependency=add_root_dependency, config=dependency_config)
                bound_user_args = signature.bind_partial(value, *args, **kwargs)

                return dependency(*bound_user_args.args, **{**bound_injected_args.kwargs, **bound_user_args.kwargs})
        
        return (scope, DependencyFactory, resolve)
    
DependencyInjectorFactory = cast(Type[IDependencyInjectorFactory], DependencyInjector)