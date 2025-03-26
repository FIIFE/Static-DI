import inspect
from typing import Callable, get_args, get_origin
from static_di.get_signature_without_self import get_signature_without_self
from static_di.fetch_dependency import FetchDependency
from static_di.interfaces import IResolveArguments

class ResolveArguments(IResolveArguments):
    def __call__(
        self,
        value,
        scope,
        config,
        fetch_dependency = None,
        get_signature_without_self = get_signature_without_self,
        user_args = {}
    ):
        fetch_dependency_impl = fetch_dependency or FetchDependency()

        signature = get_signature_without_self(value)

        bound_args = signature.bind_partial(*(user_args.get('args') or ()), **(user_args.get('kwargs') or {}))

        params = list(signature.parameters.items())

        for index, (name, param) in enumerate(params):
            # Check if argument was already provided
            if bound_args.arguments.get(name) is not None:
                continue

            if param.annotation != inspect.Parameter.empty:

                type_count_so_far = 0
                annotation, aggregate = param.annotation, False
                if param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
                    annotation, aggregate = param.annotation, True
                elif get_origin(param.annotation) is list and get_args(param.annotation):
                    type_without_list = get_args(param.annotation)[0]
                    aggregate_value = None
                    if type_without_list.__module__ == 'builtins' or type_without_list is Callable:
                        aggregate_value = type_without_list
                    else:
                        aggregate_value = type(type_without_list)
                    if aggregate_value in config['aggregate']:
                        annotation, aggregate = type_without_list, True
                else:
                    type_count_so_far = sum(1 for _, param in params[:index] if param.annotation == annotation)

                dependency = fetch_dependency_impl(annotation, scope, aggregate, config['aggregate_strategy'], type_count_so_far)

                if not dependency:
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(f"Argument '{name}' of '{value.__name__}' was not provided by user, has no matching dependency and has no default value")
                    continue
                
                if param.kind == inspect.Parameter.VAR_POSITIONAL:
                    # Handle *args case by converting to tuple
                    bound_args.arguments[name] = tuple(dependency)
                elif param.kind == inspect.Parameter.VAR_KEYWORD:
                    # Handle **kwargs case by creating a dictionary with generated keys
                    bound_args.arguments[name] = {f"{config['kwarg_key_naming_func'](name, i)}": v for i, v in enumerate(dependency)}
                else:
                    # For regular parameters, assign the value directly
                    bound_args.arguments[name] = dependency

            elif param.default == inspect.Parameter.empty:
                raise ValueError(f"Argument '{name}' of '{value.__name__}' was not provided by user, has no annotation and has no default value")
        
        return value(*bound_args.args, **bound_args.kwargs)