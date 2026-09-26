1. Goal（目标） 这个 MCP server 的根本目的是什么？
让 AI 能帮用户通过 Spotify 查询音乐流派和发现同类歌曲
2. Definitions（定义） AI 需要知道哪些前置概念？
MCP: Model Context Protocol (模型上下文协议)。由 Anthropic 推出的开放标准，旨在标准化 LLM（大语言模型）与外部数据源及工具之间的交互。它允许开发者通过统一的接口将 AI 注入现有的工作流。
MCP Server:MCP 服务端。实现 MCP 协议的独立运行程序。它负责封装底层复杂的业务逻辑（如调用 Spotify API），并向 AI 客户端暴露可用的工具清单。
Spotify API:Spotify Web API。基于 REST 架构的服务接口，允许开发者通过 HTTP 请求获取 Spotify 的音乐元数据（歌单、歌手、流派）并控制用户播放设备。
Genre Labels:流派标签。关联在音乐人（Artist）或专辑上的分类元数据。在 API 交互中，用于对曲目进行聚类分析或执行基于风格的过滤查询（如 J-Pop, Classical）。
Client ID:客户端标识符。应用程序在 Spotify 开发者平台注册后的公开身份标识。在执行 OAuth 2.0 授权流程时，用于告知服务端请求的发起方身份。
Client Secret:客户端密钥。与 Client ID 配对使用的私密字符串。用于服务端之间的身份验证，确保只有授权的应用服务器才能获取 Access Token。严禁在前端代码或公开代码库中硬编码。
3. Plan（计划） 高层次的实现步骤是什么？
阶段一：基础配置与鉴权
注册环境： 在 Spotify Developer Dashboard 创建 App，获取 Client ID 和 Client Secret。
协议搭建： 使用 Python (FastMCP) 或 Node.js 初始化 MCP Server 基础架构。
身份认证： 实现 OAuth 2.0 认证流（建议使用 Client Credentials Flow），确保 Server 具备 API 访问权限。
阶段二：核心工具实现 
4. 工具三（流派列表）： 调用接口，返回 Spotify 原生流派标签。 
5. 工具二（流派搜歌）： 封装 /v1/search 接口，通过 q=genre 参数搜索，并利用 offset 随机抽取 10 首歌曲。 
6. 工具一（歌曲查流派）： * 逻辑：搜索歌曲 ID → 获取所属 artist_id → 查询艺人详情 → 提取 genres 列表。
阶段三：集成与测试 
7. 链路联调： 在 claude_desktop_config.json 或 Cursor 中接入该 Server。
8. 场景验证： * 验证场景 1：点击流派是否准确反馈 10 首随机歌曲。 * 验证场景 2：输入歌曲名，AI 是否能通过“查流派”+“搜歌”完成链式推理。 
9. 异常处理： 针对“无流派标签艺人”或“搜索无结果”编写兜底逻辑。

4. Source Files（源文件） 必须改或创建哪几个文件？
week3/server/main.py
week3/README.md
.env 

5. Test Cases（测试） 如何验证每个工具工作正常？
提示：每个工具写1-2个具体的测试输入和预期输出
工具一：查歌曲的流派
输入："Blinding Lights"
预期输出：应该返回包含 "pop" 或 "synth-pop" 的流派列表
边界测试：输入一个不存在的歌名 "asdfghjkl"，应该返回错误提示而不是崩溃
边界测试：输入一个重名的歌名 "I love you"，应该返回所有歌名为 "I love you"关联的所有流派
边界测试：输入一首由复数个歌手演唱的歌名 "快乐崇拜"，应该返回复数歌手分别代表的流派

工具二：按流派搜索歌曲 (Search Songs by Genre)
输入： 流派名（如 "j-pop"）
内部： 调用 search 接口 → 构造查询语句 q=genre:"流派名" → 获取随机10 结果。
预期输出： 返回 10 首该流派随机抽取的歌曲列表（包含歌名及艺人）。
边界测试 1：不存在的流派
输入："Mars-Rock"
预期：返回错误提示：“未找到该流派，是否尝试查找相关流派？”或提示调用工具三查看可用列表。
边界测试 2：大小写与特殊字符
输入："Hip-Hop" 或 "hip hop"
预期：内部逻辑应进行归一化处理，确保都能正确触发 Spotify API 匹配。
边界测试 3：极其冷门的流派
输入：一个真实存在但歌曲极少的流派（如某些极细分的民谣）。
预期：如果不足 10 首，则返回所有找到的歌曲，而不是强行补全或崩溃。

工具三：查询所有可用流派 (List Available Genres)
输入： 无（或可选的关键词过滤）
内部： 使用硬编码的流派列表，不调用 API。列表直接存在代码里作为常量。
[
    "acoustic",
    "afrobeat",
    "alt-rock",
    "alternative",
    "ambient",
    "anime",
    "black-metal",
    "bluegrass",
    "blues",
    "bossanova",
    "brazil",
    "breakbeat",
    "british",
    "cantopop",
    "chicago-house",
    "children",
    "chill",
    "classical",
    "club",
    "comedy",
    "country",
    "dance",
    "dancehall",
    "death-metal",
    "deep-house",
    "detroit-techno",
    "disco",
    "disney",
    "drum-and-bass",
    "dub",
    "dubstep",
    "edm",
    "electro",
    "electronic",
    "emo",
    "folk",
    "forro",
    "french",
    "funk",
    "garage",
    "german",
    "gospel",
    "goth",
    "grindcore",
    "groove",
    "grunge",
    "guitar",
    "happy",
    "hard-rock",
    "hardcore",
    "hardstyle",
    "heavy-metal",
    "hip-hop",
    "holidays",
    "honky-tonk",
    "house",
    "idm",
    "indian",
    "indie",
    "indie-pop",
    "industrial",
    "iranian",
    "j-dance",
    "j-idol",
    "j-pop",
    "j-rock",
    "jazz",
    "k-pop",
    "kids",
    "latin",
    "latino",
    "malay",
    "mandopop",
    "metal",
    "metal-misc",
    "metalcore",
    "minimal-techno",
    "movies",
    "mpb",
    "new-age",
    "new-release",
    "opera",
    "pagode",
    "party",
    "philippines-opm",
    "piano",
    "pop",
    "pop-film",
    "post-dubstep",
    "power-pop",
    "progressive-house",
    "psych-rock",
    "punk",
    "punk-rock",
    "r-n-b",
    "rainy-day",
    "reggae",
    "reggaeton",
    "road-trip",
    "rock",
    "rock-n-roll",
    "rockabilly",
    "romance",
    "sad",
    "salsa",
    "samba",
    "sertanejo",
    "show-tunes",
    "singer-songwriter",
    "ska",
    "sleep",
    "songwriter",
    "soul",
    "soundtracks",
    "spanish",
    "study",
    "summer",
    "swedish",
    "synth-pop",
    "tango",
    "techno",
    "trance",
    "trip-hop",
    "turkish",
    "work-out",
    "world-music",
]
预期输出： 返回 Spotify 官方支持的所有流派标签数组（共约 120+ 个）。
边界测试 1：网络/API 故障
预期：如果在获取实时列表时失败，应返回一套预设的“常用流派列表”（缓存机制），并提示“当前为离线模式”。
边界测试 2：长列表处理
预期：由于流派较多，返回给 AI 客户端时应保证格式整齐（如按字母排序），方便 AI 进行二分查找或二次推荐。
边界测试 3：关键词搜索流派
输入（可选参数）："pop"
预期：仅返回包含 "pop" 字样的流派（如 k-pop, pop-film, synth-pop），提高交互效率。

6. Edge Cases（边界） 发生异常时怎么处理？
同名歌曲处理 (Duplicate Song Titles): 当搜索如 "I love you" 这种极高频歌名时，系统将检索 API 返回的所有匹配结果。工具会遍历每一个同名音轨，提取所有相关艺人的流派标签并进行去重汇总，确保返回的流派列表涵盖了所有名为 "I love you" 的歌曲所涉及的风格。
名字拼错或模糊搜索 (Typos & Fuzzy Matching) 如果用户输入 "Billie Elish"（漏写 i），系统将依赖 Spotify API 的内置模糊匹配机制。若结果为空，工具将返回：“未找到精确匹配，您是否在找 [Spotify 推荐的最接近项]？”
艺人无流派标签 (Artists without Genre Labels) 针对某些独立音乐人或刚出道艺人，其资料页可能为空，则返回 “Indie/Unknown”。
流派名称不存在 (Non-existent Genres) 当用户输入 Spotify 不支持的自定义流派（如 "Mars Rock"）时，将提示：“该流派不受支持，请尝试 [最接近的合法流派]”。
多名歌手协作 (Collaborations) 对于“快乐崇拜”这类有多个歌手的歌曲，工具一将遍历 所有参与歌手 的 ID，分别获取他们的流派标签并汇总。这能确保返回的流派既包含潘玮柏的，也包含张韶涵的。
API 频率限制 (Rate Limiting) 如果短时间内请求过多触发 429 错误，Server 将读取 Header 中的 Retry-After 字段。系统不会直接崩溃，而是会进入一个短暂的等待队列并向 AI 反馈：“服务器繁忙，请在 X 秒后重试”。
API 超时或断网 (Timeout & Network Failure) 所有请求都将设置硬性超时时间（建议 5-8 秒）。如果超过时间未收到 Spotify 回复，系统将截断请求并抛出错误信息：“网络连接超时，请检查 API 状态或本地网络”。
Token 过期 (Auth Token Expiration) 在每次调用工具前，Server 会检查 Access Token 的有效期。如果 Token 已过期或即将过期，系统将自动触发 Refresh Token 逻辑进行静默更新，确保用户感知不到授权中断。
7. Out-of-scope（范围外） 绝对不要碰什么功能？
不做播放功能、不做用户登录、不做播放列表管理
8. Extensions（未来扩展） 未来可能加什么？
推荐功能、基于心情推荐流派、基于书推荐流派
