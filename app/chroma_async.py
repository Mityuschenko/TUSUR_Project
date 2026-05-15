
# Чтобы работа с Chroma была корректной, наследуемся от базового класса Chroma с добавлением поддержки асинхронного удаления

from typing import Any

from langchain_chroma import Chroma


class AsyncChroma(Chroma):
    """Async Chroma."""

    async def adelete(self, *args: Any, **kwargs: Any) -> bool | None:
        """Async delete by vector ID or other criteria."""
        return await super().adelete(*args, **kwargs)

