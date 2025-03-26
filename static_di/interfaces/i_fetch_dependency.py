from abc import ABC
from typing import TYPE_CHECKING, Any, List, Optional, Type, Union

if TYPE_CHECKING:
    from static_di.interfaces import IScope, AggregateStrategyType

class IFetchDependency(ABC):
    def __call__(
        self,
        requested_type: Type[Any],
        scope: "IScope",
        aggregate: bool,
        aggregate_strategy: "AggregateStrategyType",
        index_of_dep_to_fetch: int = ...
    ) -> Optional[Union[Any, List[Any]]]: ...