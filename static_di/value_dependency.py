from static_di.interfaces import IValueDependency

class ValueDependency(IValueDependency):
    def __init__(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value

    def resolve(self):
        return self._value