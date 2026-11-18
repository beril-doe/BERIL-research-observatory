"""Provider abstraction for the chat feature.

Every provider emits a uniform :class:`TurnEvent` stream, regardless of the
underlying wire protocol or SDK. Route handlers consume this stream, persist
message rows, and (later) translate it into SSE frames for the browser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Literal, Protocol, runtime_checkable

from app.chat.config import ProviderConfig


# ---------------------------------------------------------------------------
# Turn events
# ---------------------------------------------------------------------------


@dataclass
class SessionInitialized:
    """Emitted once per turn, early in the stream.

    Carries the provider-assigned ``sdk_session_id`` so the caller can
    persist it on :class:`ChatSession` for future resumes.
    """

    kind: Literal["session_initialized"] = "session_initialized"
    sdk_session_id: str = ""


@dataclass
class TextDelta:
    """A chunk of assistant text.

    Providers that only deliver complete messages (non-streaming SDKs) emit
    one :class:`TextDelta` per message; streaming providers emit many.
    """

    text: str
    kind: Literal["text_delta"] = "text_delta"


@dataclass
class ToolCall:
    """The model invoked a tool."""

    name: str
    input: dict[str, Any] = field(default_factory=dict)
    tool_use_id: str | None = None
    kind: Literal["tool_call"] = "tool_call"


@dataclass
class ToolResult:
    """The result returned by a tool invocation."""

    tool_use_id: str | None
    content: Any
    is_error: bool = False
    kind: Literal["tool_result"] = "tool_result"


@dataclass
class TurnComplete:
    """Final event of a successful turn.

    ``usage`` is the provider's token accounting for the turn (``input_tokens``,
    ``output_tokens``, cache fields) and ``cost_usd`` its own cost figure,
    when it reports them — what the wiki Ask quota settles against.
    """

    kind: Literal["turn_complete"] = "turn_complete"
    result_subtype: str | None = None
    usage: dict[str, Any] | None = None
    cost_usd: float | None = None


@dataclass
class ErrorEvent:
    """Terminal event for a failed turn.

    ``usage`` and ``cost_usd`` are as on :class:`TurnComplete`: a turn can
    fail after billable work (e.g. hitting its agent-loop cap), and the wiki
    Ask quota must count that work too.
    """

    message: str
    kind: Literal["error"] = "error"
    usage: dict[str, Any] | None = None
    cost_usd: float | None = None


TurnEvent = (
    SessionInitialized | TextDelta | ToolCall | ToolResult | TurnComplete | ErrorEvent
)


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------


@dataclass
class Credentials:
    """User-supplied credentials for a single turn.

    Keyed by the ``id`` of each :class:`~app.chat.config.CredentialField`
    declared on the provider. Values never leave per-request scope.
    """

    values: dict[str, str]

    def require(self, field_id: str) -> str:
        if field_id not in self.values or not self.values[field_id]:
            raise ValueError(f"missing credential {field_id!r}")
        return self.values[field_id]


# ---------------------------------------------------------------------------
# Agent profile
# ---------------------------------------------------------------------------


@dataclass
class AgentProfile:
    """How a turn's agent is shaped, beyond the user's prompt.

    ``None`` (the default profile) is the general chat: the SDK's own system
    prompt, every built-in tool and skill. A profile replaces the system
    prompt, restricts the tools to ``allowed_tools`` (built-ins off), mounts
    the in-process MCP servers in ``mcp_servers`` and bounds the agent loop at
    ``max_turns`` — one turn per tool call, so this is the tool-call cap.
    """

    system_prompt: str
    allowed_tools: list[str] = field(default_factory=list)
    mcp_servers: dict[str, Any] = field(default_factory=dict)
    max_turns: int | None = None


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class ChatProvider(Protocol):
    """Async generator of :class:`TurnEvent` for one chat turn."""

    provider_id: str
    config: ProviderConfig

    def run_turn(
        self,
        *,
        user_message: str,
        credentials: Credentials,
        model: str,
        cwd: str,
        sdk_session_id: str | None,
        profile: AgentProfile | None = None,
    ) -> AsyncIterator[TurnEvent]:
        """Run a single chat turn and yield events as they happen.

        Implementations must yield a :class:`SessionInitialized` event once
        the provider reports a session id, and a terminal
        :class:`TurnComplete` or :class:`ErrorEvent` exactly once.
        """
        ...
