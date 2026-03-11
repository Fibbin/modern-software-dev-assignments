# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Fibbin　**Liu Liu**
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **3h45min** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
帮我写一个完整的函数extract_action_items_llm()。从input里提取action items。用 structured outputs 保证它返回的是 JSON 列表而不是随意的文字。我用Ollama的llama3.2，因此指定 JSON schema 的参数名为format,用 Pydantic 的 BaseModel定义格式。函数应该返回 List[str]
TODO
TODO 1 — 把里面笨的提取规则换成 LLM done

Generated Code Snippets:
week2/app/services/extract.py, lines 97-177（新增 _ActionItemsSchema 和 extract_action_items_llm 函数）

TODO: List all modified code files with the relevant line numbers.
TODO 2 — 给新写的 LLM 函数写测试 done


### Exercise 2: Add Unit Tests
Prompt: 
在test_extract.py里给extract.py中的函数 extract_action_items_llm() 写测试。用 Mock 替代真实的 Ollama 调用，文件顶部需要加import。要求覆盖这这几种情况：
正常输入：有 bullet points 的笔记
关键词开头：比如 "TODO: finish report"
空输入：传入空字符串
没有 action items：只是一段描述性文字
TODO
``` 

Generated Code Snippets:
eek2/app/services/test_extract.py, lines 2-4; line 7; line 24-92
TODO: List all modified code files with the relevant line numbers.
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
重构action_items.py，notes.py，main.py，db.py这四个文件。1.现在所有的输入输出都用 Dict[str, Any]，意思是"任何东西都行"。这很不安全，也不清晰。用Pydantic schema。2. main.py — init_db() 位置不对
应该用 FastAPI 的 lifespan 来管理启动逻辑，而不是直接在顶层调用。
3. db.py — 路径硬编码
DB_PATH 应该可以从环境变量读取，方便测试和部署。
4. 错误处理不完整
比如 mark_done 里，如果 action_item_id 不存在，现在不会报错，会默默什么都不做。
TODO 
把代码整理得更整洁

Generated/Modified Code Snippets:
week2/app/services/extract.py, lines 96-176（新增 _ActionItemsSchema + extract_action_items_llm()：用 Pydantic JSON schema 通过 Ollama format 强制结构化输出并解析为 List[str]，失败则 fallback）

week2/tests/test_extract.py, lines 23-91（新增 4 个单测：用 Mock 替代 Ollama 调用，覆盖 bullets / TODO: 关键词 / 空输入 / 无 action items）

week2/app/db.py, lines 14-40（新增 DB_PATH 环境变量配置与父目录创建逻辑，让 SQLite 路径可测试/可部署且支持 :memory:）

week2/app/main.py, lines 14-20（新增 FastAPI lifespan：把 init_db() 移到启动生命周期里执行，避免模块顶层副作用）

week2/app/routers/action_items.py, lines 15-45（新增 Pydantic 请求/响应模型并为 mark_done 的“ID 不存在”提供明确的 404 错误路径）

week2/app/routers/notes.py, lines 12-20（新增 Pydantic 请求/响应模型：NoteCreateRequest 与 NoteResponse，替代不安全的 Dict[str, Any]）

TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
后端（action_items.py）：
新加一个 endpoint /action-items/extract-llm，调用 extract_action_items_llm()
新加一个 endpoint /notes（GET），返回所有笔记
前端（index.html）：
新加一个 "Extract LLM" 按钮，调用 /action-items/extract-llm
新加一个 "List Notes" 按钮，调用 /notes，显示所有笔记。"List Notes" 按钮收到数据之后，页面上按顺序显示抽出的action items，并在每一个action-items后随即生成一个颜文字。
颜文字功能没有实现，查一下哪里出了问题，哪几个文件需要修改
前端的List Notes功能有误。应该在按了之后只显示过去输入过的笔记本身，原本的记录，没有任何加工，支持最多保存13个过去的笔记。

TODO
加新按钮、新功能

Generated Code Snippets:
Modified files (via git diff --stat):
- week2/app/db.py
- week2/app/main.py
- week2/app/routers/action_items.py
- week2/app/routers/notes.py
- week2/app/services/extract.py
- week2/frontend/index.html
- week2/tests/test_extract.py
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
自动生成这个Action Item Extractor项目的说明文档。README要中英双语，谢谢。
TODO
用 Cursor 自动生成这个项目的说明文档
Generated Code Snippets:
`Generated file:
- week2/README.md (newly created)
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 