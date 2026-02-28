from typing import Optional

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text


class Effect(Text):
    def __init__(
        self,
        effect_id: str,
        when: Optional[WhenCondition] = None,
    ) -> None:
        super().__init__(when)
        self.effect_id = effect_id

    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        setattr(manager, "message_effect_id", self.effect_id)
        return ""