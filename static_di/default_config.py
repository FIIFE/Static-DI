from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from static_di.interfaces import IConfig

default_config: "IConfig" = {
    'aggregate': {type},
    'aggregate_strategy': "self_scope",
    'kwarg_key_naming_func': lambda arg_name, index: f"{arg_name}_{index}"
}
