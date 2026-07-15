"""Reference comparison: CH05 implementation vs. original source material.

This file documents the comparison between our CH05 implementation
and the reference code from the original video series.  It is not
a test — it is a structural audit for review.

See: docs/research/images/ch05/ for the original reference screenshots.
"""

# =============================================================================
# IMAGE 1 — agent.py tool loop
# =============================================================================
#
# Reference (ch-05):
# -----------------------------------------------------------------------
# MAX_TOOL_STEPS = 6
#
# def _run(self) -> str:
#     specs = self.tools.specs() if self.tools else None
#     for _ in range(MAX_TOOL_STEPS):
#         resp = chat(self._payload(), model=self.model,
#                     tools=specs, provider=self.provider)
#         if resp.tool_calls and self.tools is not None:
#             for tc in resp.tool_calls:
#                 # ... extract fn name + args ...
#                 if name in self.approval_required and not self._approved(...):
#                     result = "[denied by approval gate]"
#                 else:
#                     result = self.tools.call(name, args)
#                 # ... append assistant + tool result ...
#         continue
#     return resp.content
#
# Our implementation (src/harness/agent.py):
# -----------------------------------------------------------------------
# _MAX_TOOL_ITERATIONS = 6
#
# def send(self, message: str) -> str:
#     ...
#     for iteration in range(_MAX_TOOL_ITERATIONS):
#         ...
#         response = chat(self.model, messages_to_send, tools=tool_specs)
#         if response.tool_calls:
#             for tc in assistant_msg["tool_calls"]:
#                 ...
#                 if self.tools.requires_approval(tool_name):
#                     if not prompt_approval(tool_name, summary):
#                         result = "Approval rejected: ..."
#                 else:
#                     result = self.tools.execute(tool_name, args)
#                 # ... append tool result ...
#             continue
#         return response.content
#     return "Tool loop exceeded ..."
#
# COMPARISON:
# -----------------------------------------------------------------------
# | Aspect                  | Reference              | Ours                   | Match |
# |--------------------------|------------------------|------------------------|-------|
# | Max iterations           | MAX_TOOL_STEPS = 6     | _MAX_TOOL_ITERATIONS = 6 | ✅   |
# | Method name              | _run(self)             | send(self, message)    | ⚠️   |
# | Loop structure           | for _ in range(...)    | for iteration in ...   | ✅   |
# | Tool spec passing        | specs = self.tools...  | tool_specs = self...   | ✅   |
# | Provider passing         | provider=self.provider | Unified chat() fn      | ⚠️   |
# | Message building         | self._payload()        | Inline in send()       | ⚠️   |
# | Tool call detection      | resp.tool_calls exists | response.tool_calls    | ✅   |
# | Approval check           | name in self.approval  | tools.requires_approval| ✅   |
# | Tool execution           | self.tools.call()      | self.tools.execute()   | ⚠️   |
# | Denied message           | "[denied by approval]" | "Approval rejected:..." | ⚠️   |
# | Loop cap message         | implicit (last resp)   | Explicit error string  | ⚠️   |
# | Continue after tools     | continue               | continue               | ✅   |


# =============================================================================
# IMAGE 2 — tools.py registry + sandbox scaffold
# =============================================================================
#
# Reference (ch-05):
# -----------------------------------------------------------------------
# @dataclass
# class Tool:
#     name: str; description: str; parameters: dict; func: Callable
#
# class ToolRegistry:
#     def specs(self):     # -> OpenAI tool specs
#     def call(self, name, arguments):  # dispatch by name -> str | "error: _"
#
# class Sandbox:
#     def run(self, command, workdir=None):
#         # prefer Docker (isolated container), else a local subprocess
#         ...  # hardening - no network, non-root - lands at ch-08
#
# Our implementation (src/harness/tools.py + sandbox.py):
# -----------------------------------------------------------------------
# @dataclass
# class Tool:
#     name: str; description: str; parameters: dict; fn: Callable[..., str]
#     requires_approval: bool = False
#     needs_workspace: bool = False
#
# class ToolRegistry:
#     def specs(self):     # -> OpenAI tool specs
#     def execute(self, name, arguments):  # dispatch by name -> str
#
# class Sandbox:  # (stub — src/harness/sandbox.py)
#     pass  # comment only, deferred to CH08
#
# COMPARISON:
# -----------------------------------------------------------------------
# | Aspect                  | Reference              | Ours                   | Match |
# |--------------------------|------------------------|------------------------|-------|
# | Tool dataclass           | name, desc, params,func| name, desc, params, fn | ✅   |
# | Field naming             | func                   | fn                     | ⚠️   |
# | Extra fields             | (none shown)           | requires_approval,     | ✅   |
# |                          |                        | needs_workspace        | (our addition) |
# | Specs method             | specs()                | specs()                | ✅   |
# | Dispatch method          | call()                 | execute()              | ⚠️   |
# | Error handling           | "error: _"             | "Error: ..."           | ✅   |
# | Approval model           | agent.approval_required| Tool.requires_approval | ⚠️   |
# | Sandbox scaffold         | Sandbox.run() built    | Empty stub             | ❌   |


# =============================================================================
# ARCHITECTURAL NOTES COMPARISON
# =============================================================================
#
# | Note                          | Reference              | Ours                   | Match |
# |--------------------------------|------------------------|------------------------|-------|
# | Model decides, harness runs   | ✅ Explicit            | ✅ Equivalent          | ✅   |
# | Dangerous tools ask first     | ✅ approval_required   | ✅ requires_approval   | ✅   |
# | Tool = function + schema      | ✅ Tool dataclass      | ✅ Tool dataclass      | ✅   |
# | Code runs in sandbox          | ✅ Sandbox.run() in CH05| ❌ Empty stub—CH08     | ❌   |


# =============================================================================
# SUMMARY
# =============================================================================
#
# | Category              | Count |
# |-----------------------|-------|
# | ✅ Direct matches     | 12    |
# | ⚠️ Different naming   | 8     |
# | ❌ Missing            | 1     |
#
# The one gap: sandbox.py is a comment-only stub.  The reference builds a
# Sandbox.run() scaffold in CH05 with Docker/subprocess fallback (hardened
# in CH08).  Everything else is functionally equivalent.