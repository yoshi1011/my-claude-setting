#!/usr/bin/env bash
# orchestrator をサブエージェントとして起動しようとしたときに拒否する。
# orchestrator はメインのエージェント専用（claude --agent orchestrator で起動する）。

input="$(cat)"

if printf '%s' "$input" | grep -Eq '"subagent_type"[[:space:]]*:[[:space:]]*"orchestrator"'; then
  echo "orchestrator はメインのエージェント専用のため、サブエージェントとして起動できません。orchestrator で作業する場合は、指示者に claude --agent orchestrator でセッションを始め直してもらってください。" >&2
  exit 2
fi

exit 0
