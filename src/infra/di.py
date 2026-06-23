import inspect
from typing import Dict, Type, Any, Callable, Tuple, Optional

class DIContainer:
    """
    Lightweight, dependency-free DI Container.
    Maintains a mapping of interfaces to concrete implementations and handles
    recursive dependency tree resolution using Python's reflection APIs (inspect).
    """

    def __init__(self) -> None:
        self._registry: Dict[Type[Any], Tuple[Any, bool]] = {}
        self._instances: Dict[Type[Any], Any] = {}

    def register(self, interface: Type[Any], concrete: Any, singleton: bool = True) -> None:
        """
        Registers an interface mapping to a concrete class, instance, or factory function.
        If singleton is True, the resolved instance is cached and reused.
        """
        self._registry[interface] = (concrete, singleton)

    def resolve(self, interface: Type[Any]) -> Any:
        """
        Resolves the requested interface or concrete class recursively.
        """
        import typing
        origin = typing.get_origin(interface)
        # Support UnionType (for T | None in Python 3.10+) and standard typing.Union
        UnionType = getattr(typing, "UnionType", None)
        is_union = origin is typing.Union or (UnionType is not None and origin is UnionType)
        
        if is_union:
            args = typing.get_args(interface)
            non_none_args = [arg for arg in args if arg is not type(None)]
            if non_none_args:
                interface = non_none_args[0]
            else:
                return None

        if interface in self._instances:
            return self._instances[interface]

        if interface not in self._registry:
            if inspect.isclass(interface) and not inspect.isabstract(interface):
                # If it's a concrete class not registered, try to instantiate it automatically
                resolved = self._instantiate(interface)
                # By default, treat auto-resolved concrete classes as singletons to preserve state
                self._instances[interface] = resolved
                return resolved
            raise ValueError(f"Dependency {interface} is not registered in the container")

        concrete, singleton = self._registry[interface]

        if not inspect.isclass(concrete) and not callable(concrete):
            # If registered object is already a pre-instantiated value/object
            return concrete

        resolved = self._instantiate(concrete)

        if singleton:
            self._instances[interface] = resolved

        return resolved

    def _instantiate(self, concrete: Any) -> Any:
        if not inspect.isclass(concrete):
            if callable(concrete):
                # If it's a factory function, inspect its parameters to resolve them
                sig = inspect.signature(concrete)
                kwargs = {}
                for name, param in sig.parameters.items():
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            kwargs[name] = self.resolve(param.annotation)
                        except ValueError as e:
                            if param.default != inspect.Parameter.empty:
                                kwargs[name] = param.default
                            else:
                                raise e
                return concrete(**kwargs)
            return concrete

        # Inspect class constructor
        init_method = getattr(concrete, "__init__", None)
        if init_method is None or init_method is object.__init__:
            return concrete()

        sig = inspect.signature(init_method)
        kwargs = {}
        for name, param in sig.parameters.items():
            if name == "self":
                continue

            annotation = param.annotation
            if annotation == inspect.Parameter.empty:
                if param.default != inspect.Parameter.empty:
                    kwargs[name] = param.default
                    continue
                raise ValueError(
                    f"Cannot resolve parameter '{name}' of constructor {concrete.__name__}: "
                    "no type annotation provided"
                )

            try:
                kwargs[name] = self.resolve(annotation)
            except ValueError as e:
                if param.default != inspect.Parameter.empty:
                    kwargs[name] = param.default
                else:
                    raise e

        return concrete(**kwargs)
