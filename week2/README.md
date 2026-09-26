# Week 2 — Action Item Extractor（中英双语 / Bilingual）

将自由格式笔记转换为可勾选的 action items 清单的最小应用：**FastAPI + SQLite**。  
同时提供基于规则的提取器，以及基于 **Ollama structured outputs** 的 **LLM 提取器**。

A minimal **FastAPI + SQLite** app that turns free-form notes into a checklist of action items.  
Includes a heuristic extractor and an **LLM-powered extractor** via **Ollama structured outputs**.

## 快速开始 / Quickstart

在仓库根目录（确保已激活 conda 环境 `cs146s`）运行：

From the repo root (with your conda env `cs146s` activated), run:

```bash
poetry install
poetry run uvicorn week2.app.main:app --reload
```

然后打开 `http://127.0.0.1:8000/`。

Then open `http://127.0.0.1:8000/`.

## 前端 / Frontend

前端是一个静态页面 `week2/frontend/index.html`，由后端直接提供：

The UI is a single static file at `week2/frontend/index.html` served by the backend:

- **Extract**：调用基于规则的提取接口。
- **Extract LLM**：调用 Ollama/LLM 提取接口。
- **List Notes**：拉取最近保存的最多 13 条笔记，并原样显示笔记内容（不做任何加工）。

- **Extract**: calls the heuristic extractor endpoint.
- **Extract LLM**: calls the Ollama/LLM extractor endpoint.
- **List Notes**: fetches up to the last 13 saved notes and displays their raw content (no processing).

## API（接口说明 / API Reference）

### `POST /action-items/extract`
用基于规则的提取器抽取 action items。

Extract action items with the heuristic extractor.

**请求 / Request**

```json
{ "text": "string", "save_note": true }
```

**响应 / Response**

```json
{
  "note_id": 123,
  "items": [{ "id": 1, "text": "Set up database" }]
}
```

### `POST /action-items/extract-llm`
使用 `extract_action_items_llm()` 抽取 action items（Ollama + structured outputs）。

与 `/action-items/extract` 的请求/响应结构相同。

Extract action items using `extract_action_items_llm()` (Ollama + structured outputs).

Same request/response shape as `/action-items/extract`.

### `GET /action-items`
列出已保存的 action items（可按 `note_id` 过滤）。

Query params / 查询参数：
- `note_id`（可选 int / optional int）

### `POST /action-items/{action_item_id}/done`
将某条 action item 标记为完成/未完成。

Mark an action item done/undone.

**请求 / Request**

```json
{ "done": true }
```

如果 `action_item_id` 不存在会返回 `404`。

Returns `404` if `action_item_id` does not exist.

### `POST /notes`
创建一条笔记。

Create a note.

**请求 / Request**

```json
{ "content": "string" }
```

### `GET /notes`
列出笔记（按时间从新到旧）。

List notes (most recent first).

Query params / 查询参数：
- `limit`（可选 int，默认 `13` / optional int, default `13`）

## 配置（环境变量）/ Configuration (Environment Variables)

### `OLLAMA_MODEL`
LLM 提取器使用的模型名。

LLM model name for the LLM extractor.

- 默认 / Default：`llama3.2`

示例 / Example:

```bash
set OLLAMA_MODEL=llama3.2
```

需要确保 Ollama 在运行，并且已拉取模型，例如：

You must have Ollama running and the model pulled, e.g.:

```bash
ollama pull llama3.2
```

### `DB_PATH`
SQLite 数据库路径（便于测试与部署）。

SQLite database path (useful for testing/deployments).

- 默认 / Default：`week2/data/app.db`
- 支持 / Supports：`:memory:`（内存数据库 / in-memory DB）

示例 / Example:

```bash
set DB_PATH=:memory:
```

## 运行测试 / Running Tests

```bash
poetry run pytest week2/tests
```

