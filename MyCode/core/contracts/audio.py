from abc import ABC, abstractmethod


class IAudioProvider(ABC):
    @abstractmethod
    def generate(self, uid: str, content: str) -> str:
        """Generate audio and return file path."""


class IAudioGenerationService(ABC):
    @abstractmethod
    def create_voice(self, uid: str, content: str) -> str:
        """Create voice file and return output path."""
