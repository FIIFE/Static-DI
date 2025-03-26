from abc import ABC
import inspect
from typing import Any, Callable, Dict, Optional, Type, TypedDict
from static_di.interfaces import IScope, IConfig, IFetchDependency

class UserArgs(TypedDict, total=False):
    args: tuple[Any, ...]
    kwargs: Dict[str, Any]

class IResolveArguments(ABC):
    def __call__(
        self,
        value: Type,
        scope: IScope,
        config: IConfig,
        fetch_dependency: Optional[IFetchDependency] = None,
        get_signature_without_self: Callable[[Type], inspect.Signature] = ...,
        user_args: UserArgs = ...
    ): ...