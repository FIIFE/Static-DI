# Static-DI

A type-based dependency injection library with scoping capabilities. It allows dependencies to be registered within a hierarchical scope structure and requested via type annotations.

## Features

### Type-Based Dependency Injection
Dependencies are requested in class constructors via parameter type annotations, allowing them to be matched based on their type, class, or base class.

### Scoping
Since registered dependencies can share a type, using a flat container to manage dependencies can lead to ambiguity. To address this, the library uses a hierarchical scope structure to precisely control which dependencies are available in each context.

### Dependencies as Dependents in Different Scopes
A class can act as a dependency in one scope while being a dependent in another. This enables layered designs where components can both consume and provide services across different scopes.

### No Tight Coupling with the Library Itself
Dependency classes remain clean and library-agnostic. No decorators, inheritance, or special syntax are required. This ensures your code stays decoupled from the library, making it easier to test, reuse, and maintain.

### Resolution Strategies
Choose how each dependency is resolved based on your use case:

- **Singleton** – A single instance is created and shared across all dependents.
- **Instances** – Returns a new instance each time the dependency is requested.
- **Factory** – Returns the class itself, wrapped in a dependency-aware wrapper. Useful for manual instantiation with injected defaults. Request it via `Type[MyClass]`.

### Multiple Dependency Injection
Multiple dependencies of the same type can be injected using the following patterns:

- **arg1: \<type\>, arg2: \<type\>** - When multiple parameters share the same type, distinct dependencies of that type will be passed to each one, following the order in which the dependencies were registered.
- **List[\<type\>]** – If \<type\> exists in config.aggregate then aggregates all dependencies of type \<type\> and returns them as a list. Otherwise it looks for one specific dependency of type List[\<type\>].
- **\*args: \<type\>** – Packs all matching dependencies into positional arguments.
- **\*\*kwargs: \<type\>** – Packs all matching dependencies into keyword arguments. Keys are determined by a customizable `config.kwarg_key_naming_func`.

### Configurable Behavior
Define the resolution behaviour either globally or per dependency using a config.

- **config.aggregate** – Controls which types should be aggregated.
- **config.aggregate_strategy** – Determines whether aggregated dependencies (e.g. in lists) should be resolved only from the current scope or also include parent scopes.
- **config.kwarg_key_naming_func** – Controls the keys used when injecting multiple dependencies via `**kwargs`.

## Basic Example
```python
# service.py
from abc import ABC

class IService(ABC): ...
class Service(IService): ... # define Service to be injected
```
```python
# consumer.py
from service import IService

class Consumer:
    def __init__(self, service: IService): ... # define Consumer with Service dependency request via base class type
```
```python
# main.py
from static_di import DependencyInjector
from consumer import Consumer
from service import Service

Scope, Dependency, resolve = DependencyInjector() # initiate dependency injector

Scope(
    dependencies=[
        Dependency(Consumer, root=True), # register Consumer as a root Dependency (root dependencies serve only as dependents)
        Dependency(Service) # register Service dependency that will be passed to Consumer
    ]
)

resolve() # start dependency resolution process
```
## Installation
### pip
```
pip install static_di
```
### uv
```
uv add static_di
```
## API
### `DependencyInjector(config: IPartialConfig = default_config) -> (IScope, IDependencyFactory, Callable[[], None])`
Creates a dependency injector that connects all parts of the system and allows passing a global configuration.

#### Parameters:
- `config: IPartialConfig = default_config` - Global configuration for dependency resolution. Defaults to default_config. Omitted properties are filled with defaults.
#### Returns:
- `Scope: IScope` - A class for building hierarchical scope structure.
- `Dependency: IDependencyFactory` - A factory for creating Dependencies.
- `resolve: Callable[[], None]` - A function that triggers the resolution process starting from the `root=True` entry dependency.
### `IPartialConfig`
Optional configuration settings that control how dependency injection behaves. Can be passed globally to the dependency injector or overridden per individual dependency. Fields:
- `aggregate: Set[Any]` - A set of type annotations that determine which dependencies should be aggregated. When a parameter is annotated with one of these types, all matching dependencies will be injected as a list.
- `aggregate_strategy: Literal["self_scope", "full"]` - Defines the aggregation strategy. Use "self_scope" to limit aggregation to the current scope only, or "full" to aggregate from all available scopes.
- `kwarg_key_naming_func: Callable[[str, int], str]` - A function that determines how keyword argument keys are named when injecting aggregated dependencies via **kwargs.
### `default_config: IConfig`
The default configuration used by the dependency injector:
```python
default_config: "IConfig" = {
    'aggregate': {type},
    'aggregate_strategy': "self_scope",
    'kwarg_key_naming_func': lambda arg_name, index: f"{arg_name}_{index}"
}
```
### `DependencyFactory(value: Union[Type[Any], Any], resolve_as: Literal["singleton", "instances", "factory"] = "singleton", root: bool = False, config: IPartialConfig) -> Union[IClassDependency, IValueDependency]`
A factory function that takes a value to be registered as a dependency. Returns either IClassDependency when registering a class or IValueDependency otherwise. IClassDependency instances have their parameters resolved while IValueDependencies are returned as is.
#### Parameters:
- `value: Union[Type[Any], Any]` - The value to register as a dependency.
    
    Rest parameters apply only when value is a class.
- `resolve_as: Literal["singleton", "instances", "factory"] = "singleton"` - Defines how the dependency should be resolved. Options:
    - `singleton` – One instance shared between all dependents (default).
    - `instances` – A new instance for each request.
    - `factory` – Injects the class itself (not an instance) wrapped in a dependency injecting function.
- `root: bool = False` - If True, marks this dependency as the entry point for resolution.
- `config: IPartialConfig = None` - A typed dictionary specifying resolution behaviour of this dependency. Omitted props default to config values defined in DependencyInjector.
#### Returns:
`IClassDependency` - A class dependency instance that will have it's dependencies recursively resolved.

or

`IValueDependency` - A value dependency instance that has it's value returned as is.
### `Scope(*, scopes: List[IScope] = [], dependencies: List[Union[IClassDependency, IValueDependency]] = [], dependents: List[IClassDependency] = [])`
Defines a scope that serves as a resolution context for the dependencies registered in it.

Scopes can be nested to create a hierarchical structure that controls how dependencies are discovered and injected.
#### Parameters:
- `scopes: List[IScope] = []` - A list of child scopes nested within this one. Dependencies have access only to self scope and parent scopes.
- `dependencies: List[Union[IClassDependency, IValueDependency]] = []` - Dependencies to register within this scope. These will be available for dependents when requested from this scope or any child scope. Dependencies also serve as dependents in the same scope unless explicitly defined as dependents in other scopes.
- `dependents: List[IClassDependency] = []` - A list of dependencies that should have their own dependencies resolved within this scope. This is useful when a dependency is intended to act as a dependent in one scope while serving as a dependency in another.
## Pre-Release Notice
This library is currently in a pre-release state. APIs, behavior, and features are subject to change as development continues. Use in production environments is not recommended at this stage.
## Advenced examples
### Nested scope
```python
# i_service.py
from typing import Protocol

class IService(Protocol): ...
```
```python
# service.py
from i_service import IService

class Service(IService): ...
```
```python
# consumer.py
from i_service import IService

class Consumer:
    def __init__(self, service: IService): ...
```
```python
# main.py
from static_di import DependencyInjector
from consumer import Consumer
from service import Service

Scope, Dependency, resolve = DependencyInjector()

Scope(
    dependencies=[
        Dependency(Service) # Despite type match, this Service is not going to get passed to Consumer since it's further from it than the other Service
    ],
    scopes=[
        Scope(
            dependencies=[
                Dependency(Consumer, root=True),
                Dependency(Service) # This Service is going to get passed to Consumer since they're closest to each other in scope lookup chain
            ]
        )
    ]
)

resolve()
```
### Dependencies as Dependents in Different Scopes
```python
# service.py
class Service(): ...
```
```python
# consumer.py
from service import Service

class Consumer:
    def __init__(self, service: Service): ...
```
```python
# main.py
from static_di import DependencyInjector
from consumer import Consumer
from service import Service

Scope, Dependency, resolve = DependencyInjector()

root_dependency = Dependency(Consumer, root=True) # define root dependency outside and assign it to root_dependency variable so we can pass its reference to multiple scopes

Scope(
    dependencies=[
        Dependency(Service) # this Service will be passed to Consumer since Consumer is used in this scope as dependent
    ],
    dependents=[
        root_dependency # root_dependency is being registered in this scope as a dependent
    ]
    scopes=[
        Scope(
            dependencies=[
                root_dependency,
                Dependency(Service) # this Service will not be passed to Consumer despite it being available in this scope as a dependency
            ]
        )
    ]
)

resolve()
```
### Multiple Dependency Injection
```python
# mirror.py
class Mirror(): ...
```
```python
# wheel.py
class Wheel(): ...
```
```python
# window.py
class Window: ...
```
```python
# seat.py
class Seat: ...
```
```python
# car.py
from mirror import Mirror
from wheel import Wheel
from window import Window
from seat import Seat

class Car:
    def __init__(self, left_mirror: Mirror, right_mirror: Mirror, wheels: List[Wheel], *windows: Window, **seats: Seat):
        self.left_mirror = left_mirror # first Mirror instance registered in scope
        self.right_mirror = right_mirror # second Mirror instance registered in scope
        self.wheels = wheels # a list of 4 Wheel instances
        self.windows = windows # a tuple of 4 Window instances
        self.seats = seats # a dict of 4 Seat instances with keys 'seats_0', ..., 'seats_3' named by kwarg_key_naming_func from default_config
```
```python
# main.py
from static_di import DependencyInjector
from mirror import Mirror
from wheel import Wheel
from window import Window
from seat import Seat
from car import Car

Scope, Dependency, resolve = DependencyInjector()

Scope(
    dependencies=[
        Dependency(Car, root=True),
        Dependency(Mirror),
        Dependency(Mirror),
        Dependency(Wheel),
        Dependency(Wheel),
        Dependency(Wheel),
        Dependency(Wheel),
        Dependency(Window),
        Dependency(Window),
        Dependency(Window),
        Dependency(Window),
        Dependency(Seat),
        Dependency(Seat),
        Dependency(Seat),
        Dependency(Seat),
    ]
)

resolve()
```
### For more examples consult test_all.py file
## Limitations
- Type matching is done by the [typeguard library](https://typeguard.readthedocs.io/en/latest/index.html) so any limitation that applies to it applies here for example booleans are matched when requesting int, Callable parameter types are not respected.