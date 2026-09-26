#导入工具
from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
#定义匹配规则
#两种识别 action item 的规则
#一种是识别 -、*、1. 这类列表符号开头的行，
#另一种是识别 todo:、action:、next: 这类关键词开头的行。

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)

#判断一行是不是 action item,是就返回 True，不是就返回 False。
def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False

#主函数.整段文字拆成一行一行检查，
def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique

#判断句子是不是祈使句
def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


class _ActionItemsSchema(BaseModel):
    """
    Pydantic 模型，用于给 Ollama 提供 JSON Schema。

    约定返回格式：
    {
      "items": ["action item 1", "action item 2", ...]
    }
    """

    items: List[str]


def extract_action_items_llm(text: str) -> List[str]:
    """
    使用 Ollama + LLM 提取 action items，强制返回 List[str]。

    - 使用 Pydantic BaseModel 定义 JSON Schema
    - 通过 `format` 参数把 schema 传给 Ollama，启用 structured outputs
    """
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2")

    # 使用 Pydantic 的 JSON Schema 作为 structured output 规范
    schema: dict[str, Any] = _ActionItemsSchema.model_json_schema()

    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts concise action items from notes. "
                "Return ONLY JSON that matches the provided schema. "
                "Each item should be a short, imperative task description."
            ),
        },
        {
            "role": "user",
            "content": (
                "From the following notes, extract all concrete action items. "
                "Do not invent tasks that are not implied by the text.\n\n"
                f"NOTES:\n{text}"
            ),
        },
    ]

    try:
        response = chat(
            model=model_name,
            messages=messages,
            format=schema,
        )

        # Ollama 通常把结构化结果放在 message.content 里
        content = response.get("message", {}).get("content")

        # content 可能是 JSON 字符串，也可能已经是 dict
        if isinstance(content, str):
            parsed = json.loads(content)
        else:
            parsed = content

        if not isinstance(parsed, dict):
            raise ValueError("LLM response is not a JSON object")

        items = parsed.get("items", [])
        if not isinstance(items, list):
            raise ValueError("`items` is not a list in LLM response")

        # 只保留非空字符串，并做 strip
        cleaned_items: List[str] = []
        for item in items:
            if isinstance(item, str):
                s = item.strip()
                if s:
                    cleaned_items.append(s)

        return cleaned_items
    except Exception:
        # 如果 LLM 或解析失败，回退到基于规则的实现，保证函数稳定返回 List[str]
        return extract_action_items(text)
