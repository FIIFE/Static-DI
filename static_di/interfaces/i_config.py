from typing import Any, Callable, Literal, Set, TypedDict

AggregateStrategyType = Literal["full", "self_scope"]
class IPartialConfig(TypedDict, total=False):
    aggregate: Set[Any]
    aggregate_strategy: AggregateStrategyType
    kwarg_key_naming_func: Callable[[str, int], str]

class IConfig(IPartialConfig, total=True):
    aggregate: Set[Any]
    aggregate_strategy: AggregateStrategyType
    kwarg_key_naming_func: Callable[[str, int], str]
