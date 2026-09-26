# Week 3 — Spotify Genre MCP Server（中英双语 / Bilingual）

本周你实现了一个基于 **FastMCP** 的 Spotify 工具服务端，让 AI 客户端（如 **Claude Desktop**、Cursor MCP）可以直接调用这些工具来查流派、按歌名/流派找歌。

This week implements a **FastMCP** server that lets an AI client (e.g. **Claude Desktop**, Cursor MCP) call **Spotify tools** to:

- 列出 Spotify 支持的流派 seeds（genre seeds）
- 按歌名搜索歌曲
- 按流派搜索歌曲

The server uses the **Spotify Web API** via the **Client Credentials Flow** and exposes tools through the **Model Context Protocol (MCP)**.

---

## 1. 前置条件与安装 / Prerequisites & Installation

### 1.1 依赖 / Dependencies

在仓库根目录（week1–2 已经用过）：

From the repo root (you should already have this from week 1–2):

```bash
conda activate cs146s
poetry install
```

本周 Server 用到的核心库已经在根目录 `pyproject.toml` 里声明：

The required libraries for this server are in the root `pyproject.toml`:

- `fastmcp`
- `requests`

### 1.2 Spotify API 凭据 / Spotify API Credentials

在 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) 创建一个 App，并获取：

- **Client ID**
- **Client Secret**

然后把它们设为环境变量（或者放到 MCP 运行时会加载的 `.env` 文件里）：

```bash
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

在 macOS / Linux（bash/zsh）：

```bash
export SPOTIFY_CLIENT_ID=your_client_id_here
export SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Server 通过 `Client Credentials Flow` 使用这些凭据获取 access token。

The server uses these via `Client Credentials Flow` to obtain an access token.

---

## 2. 启动 MCP Server / Running the MCP Server

入口文件如下：

- `week3/server/main.py`（server 对象名：`mcp`）

The entrypoint is:

- `week3/server/main.py` (server object: `mcp`)

### 2.1 直接用 Python 启动 / Run directly with Python

在仓库根目录执行：

From the repo root:

```bash
cd week3/server
python main.py
```

这会以默认的 **stdio transport** 启动 FastMCP server，这是大部分 MCP 客户端（包括 Claude Desktop）期望的模式。

This runs the FastMCP server with the default **stdio transport**, which is what most MCP clients (including Claude Desktop) expect.

### 2.2 用 FastMCP CLI 启动（可选）/ Run via FastMCP CLI (optional)

如果你安装了 `fastmcp` CLI，可以这样运行：

If you have the `fastmcp` CLI installed:

```bash
cd week3/server
fastmcp run main.py:mcp
```

你也可以选择 HTTP transport 方便调试：

You can also choose an HTTP transport for debugging:

```bash
fastmcp run main.py:mcp --transport http --port 8000
```

---

## 3. 可用工具 / Available Tools

所有工具都在 `week3/server/main.py` 中定义，并通过 FastMCP 暴露给 MCP 客户端。

All tools are defined in `week3/server/main.py` and exposed via FastMCP.

### 3.1 `list_genres`

**函数签名 / Signature**

```python
list_genres(keyword: str | None = None) -> list[str]
```

**说明 / Description**

- 返回一份 **硬编码的 Spotify genre seeds 列表**（不调用 API）。
- 如果提供 `keyword`（不区分大小写），只返回包含该子串的流派。

Returns the **hardcoded list** of Spotify genre seeds (no API call).  
If `keyword` is provided (case-insensitive), only genres containing that substring are returned.

**调用示例（概念）/ Example call (conceptual)**

```jsonc
// MCP tool call
{
  "tool": "list_genres",
  "args": { "keyword": "pop" }
}
```

**响应示例 / Example response**

```json
["indie-pop", "j-pop", "k-pop", "pop", "pop-film", "synth-pop"]
```

---

### 3.2 `search_songs`

**函数签名 / Signature**

```python
search_songs(track_name: str, limit: int = 10) -> dict
```

**说明 / Description**

- 调用 Spotify `/v1/search`，参数 `q=track_name`、`type=track`。
- 返回匹配到的歌曲列表；**不会**再去查艺人流派信息。

Uses Spotify `/v1/search` with `q=track_name`, `type=track`.  
Returns a list of matching tracks; **does not** fetch artist genres.

**响应结构 / Response shape**

```json
{
  "query": "Blinding Lights",
  "tracks": [
    {
      "track_id": "0VjIjW4GlUZAMYd2vXMi3b",
      "name": "Blinding Lights",
      "artists": "The Weeknd"
    }
    // ...
  ],
  "message": "No tracks found for this name."
}
```

其中 `message` 字段只有在没有任何结果时才会出现。

`message` is only present when no tracks are found.

---

### 3.3 `search_songs_by_genre`

**函数签名 / Signature**

```python
search_songs_by_genre(genre: str, limit: int = 10) -> dict
```

**说明 / Description**

- 先把流派名归一化（小写、空格替换为 `-`），并检查是否在 `GENRE_SEEDS` 里。
- 如果合法，则用 `/v1/search` 调用 `q=genre:"{normalized}"`、`type=track`。
- 使用随机 `offset`，在该流派下抽取近似“随机”的最多 10 首歌。

Normalizes the genre (lowercase, spaces → `-`) and checks against `GENRE_SEEDS`.  
If valid, uses `/v1/search` with `q=genre:"{normalized}"`, `type=track`.  
Picks a random `offset` to approximate “random 10 tracks” in that genre.

**成功时响应结构 / Response shape (success)**

```json
{
  "genre": "j-pop",
  "normalized": "j-pop",
  "limit": 10,
  "offset": 20,
  "tracks": [
    {
      "id": "some_track_id",
      "name": "Song Title",
      "artists": "Artist A, Artist B",
      "uri": "spotify:track:some_track_id"
    }
    // ...
  ]
}
```

**不支持流派时响应结构 / Response shape (unsupported genre)**

```json
{
  "genre": "Mars-Rock",
  "normalized": "mars-rock",
  "tracks": [],
  "error": "Unsupported genre. Call list_genres first to see valid Spotify genres."
}
```

---

## 4. 接入 Claude Desktop（MCP） / Connecting to Claude Desktop (MCP)

> 不同操作系统和 Claude 版本配置路径可能略有不同，但核心思路一样：让 Claude 指向这个 MCP server 的文件和入口。

The exact configuration path may vary slightly by OS and Claude version, but the idea is the same: point Claude at the MCP server file and entrypoint.

### 4.1 Claude Desktop MCP 配置示例 / Example Claude Desktop MCP config

在 Claude Desktop 的 MCP 配置（例如 `claude_desktop_config.json` 或 `claude_config.json`）中加入类似配置：

In Claude Desktop’s MCP configuration (e.g. `claude_desktop_config.json` or `claude_config.json`), add something like:

```json
{
  "mcpServers": {
    "spotify-genre-mcp": {
      "command": "python",
      "args": [
        "c:/Users/yourname/modern-software-dev-assignments/week3/server/main.py"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

说明 / Notes:

- 在 macOS / Linux 上，需要把路径改成对应的绝对路径，例如 `/Users/you/modern-software-dev-assignments/week3/server/main.py`。
- 如果你已经在系统/终端里设置了环境变量，这里的 `env` 字段可以省略。

On macOS / Linux, adjust the path to the repo root (e.g. `/Users/you/modern-software-dev-assignments/week3/server/main.py`).  
You can also omit `env` here if you set env vars globally in your shell or system.

### 4.2 在 Claude 里如何使用这些工具 / Using the tools in Claude

重启 Claude Desktop 并成功发现这个 MCP server 后，你可以直接用自然语言引导它：

Once Claude Desktop is restarted and the server is discovered, you can ask things like:

- “用 `spotify-genre-mcp` 帮我列出所有包含 ‘pop’ 的流派。”  
  “Use the `spotify-genre-mcp` tools to list all genres that contain ‘pop’.”
- “用 Spotify MCP server 搜索歌名为 ‘Blinding Lights’ 的歌曲。”  
  “Search songs named ‘Blinding Lights’ using the Spotify MCP server.”
- “用流派工具帮我随机找 10 首 J-Pop 歌曲。”  
  “Find 10 random J-Pop songs using the genre tools.”

Claude 会自动：

- 调用 `list_genres` 来发现可用流派。
- 调用 `search_songs` 或 `search_songs_by_genre` 并传入合适的参数。

Claude should automatically:

- Call `list_genres` to discover valid genres.
- Call `search_songs` or `search_songs_by_genre` with appropriate arguments.

你可以在 Claude 的 UI 里查看工具调用轨迹（视版本而定），确认 MCP server 正在被正确使用。

You can inspect tool call traces in Claude’s UI (depending on version) to verify the MCP server is being used correctly.

---

## 5. 错误处理与边界情况 / Error Handling & Edge Cases

这个 Server 对常见异常做了一些保护：

The server implements several safety checks:

- **输入为空 / Empty input**：
  - 当核心参数为空字符串时，`search_songs` / `search_songs_by_genre` 会抛出校验错误。
- **没有结果 / No results**：
  - `search_songs` 返回空的 `tracks` 列表，并附带一条 `message`。
- **不支持的流派 / Unsupported genres**：
  - `search_songs_by_genre` 返回 `error` 字段，并建议先调用 `list_genres`。
- **频率限制（HTTP 429）/ Rate limits (HTTP 429)**：
  - 抛出带有 `Retry-After` 信息的清晰错误。
- **认证/网络错误 / Auth / network errors**：
  - 以 `RuntimeError` 形式抛出，包含 HTTP 状态码和响应体，方便在 MCP 客户端里排查。

配置好之后，Claude（或者任何 MCP 客户端）都可以稳定调用你的 Spotify 工具，按流派/歌名帮助用户探索歌曲和相似风格。

With this setup, Claude (or any MCP client) can reliably call your Spotify tools to explore genres and discover similar songs. 

