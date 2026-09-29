from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class FetchResult:
    is_success: bool
    content: str
    utc: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __str__(self) -> str:
        return f"FetchResult(is_success={self.is_success}, content_length={len(self.content)}, utc={self.utc.isoformat()})"


"""
Why not created_at: datetime = datetime.now(timezone.utc)?
If you pass the call directly without default_factory, it runs once at module load time. Every single instance created
after that would share that exact same initial timestamp.
"""
