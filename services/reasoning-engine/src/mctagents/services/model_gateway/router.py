from dataclasses import dataclass, field
from enum import StrEnum

from mctagents.services.model_gateway.base import ModelProvider


class TaskType(StrEnum):
    FRAMER = "framer"
    ARCHITECT = "architect"
    EVIDENCE = "evidence"
    CRITIC = "critic"
    JUDGE = "judge"
    SYNTHESIZER = "synthesizer"
    EMBEDDING = "embedding"


@dataclass
class ModelPreset:
    chat_model: str
    reasoning_model: str
    embedding_model: str


class ModelRouter:
    def __init__(
        self,
        providers: dict[str, ModelProvider],
        preset: ModelPreset,
        task_routing: dict[TaskType, str] | None = None,
    ):
        self.providers = providers
        self.preset = preset
        self.task_routing = task_routing or self._default_task_routing()

    def _default_task_routing(self) -> dict[TaskType, str]:
        return {
            TaskType.FRAMER: "chat",
            TaskType.ARCHITECT: "chat",
            TaskType.EVIDENCE: "chat",
            TaskType.CRITIC: "chat",
            TaskType.JUDGE: "reasoning",
            TaskType.SYNTHESIZER: "reasoning",
            TaskType.EMBEDDING: "embedding",
        }

    def select_model(self, task_type: TaskType) -> tuple[ModelProvider, str]:
        model_kind = self.task_routing[task_type]
        provider = self.providers["ollama"]

        if task_type == TaskType.EMBEDDING:
            return provider, self.preset.embedding_model
        elif model_kind == "reasoning":
            return provider, self.preset.reasoning_model
        else:
            return provider, self.preset.chat_model
