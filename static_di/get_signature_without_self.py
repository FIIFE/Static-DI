import inspect
from typing import Type

def get_signature_without_self(cls: Type):
    signature_with_self = inspect.signature(cls.__init__)
    params = list(signature_with_self.parameters.values())[1:]
    return inspect.Signature(parameters=params)