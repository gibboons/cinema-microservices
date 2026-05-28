from typing import Any, Callable, Type

class SimpleContainer:
    """Minimal DI container compatible with Diator interface."""

    def __init__(self):
        self._factories: dict[Type, Callable] = {}

    def register(self, type_: Type, factory: Callable) -> None:
        self._factories[type_] = factory

    async def resolve(self, type_: Type) -> Any:
        factory = self._factories.get(type_)
        if not factory:
            raise ValueError(f"SimpleContainer: no registration for {type_.__name__}")
        return factory()
