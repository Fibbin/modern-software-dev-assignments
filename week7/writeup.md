# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: Fibbin \
SUNet ID: **TODO** \
Citations: Gemini

This assignment took me about 8 hours to do. 


## Task 1: Add more endpoints and validations
Manual Review (人工审查): 主要检查了 DELETE 接口是否能正确拦截不存在的笔记（返回 404），并确认了 Pydantic 模型加入了字符串非空验证。

AI Review (AI 审查): AI 建议 DELETE 操作成功后严格返回 HTTP 204 No Content，而不是 200 附带 JSON。此外，AI 建议对所有涉及 DB 的操作包裹 SQLAlchemyError 的异常捕获，抛出 500 错误以防止底层结构泄露。

Comparison (对比反思): AI 比人工审查更关注严格的 RESTful 语义规范，并且在异常处理的兜底逻辑上考虑得更全面。

### Task 2: Action Item Extraction
*   **Manual Review**: 确认了正则表达式能够正确匹配时间、日期格式，并且能够从输入文本中成功提取出待办事项的字符串。
*   **AI Review**: AI 建议在正则表达式编译层面使用 `re.compile()` 提升每次调用的性能。此外，AI 提醒要考虑跨年日期（缺少具体年份时）的边缘情况，并建议对提取的返回结果增加边界裁剪（strip）以防产生多余空格。
*   **Comparison**: 人工审查更关注“功能跑通”，AI 审查则对正则的运行效率和极端文本边界情况考虑得更细致。

### Task 3: Tag Model & Many-to-Many Relationship
*   **Manual Review**: 检查了中间关联表（association table）的建立，并测试了给 Note 添加/解除标签的 API 是否能正常进行数据库交互。
*   **AI Review**: AI 审查重点指出了 ORM 常见的 N+1 查询性能问题，建议在 SQLAlchemy 查询时使用 `selectinload` 进行预加载（eager loading）。同时，AI 建议在模型层面明确配置 `cascade="all, delete"`，防止删除笔记时产生底层的脏数据。
*   **Comparison**: 人工审查侧重于数据模型是否关联成功，AI 则直接切中了数据库操作中最容易忽略的性能陷阱（N+1 问题）和数据一致性隐患。

### Task 4: Pagination, Sorting & Tests
*   **Manual Review**: 确认了 `limit` 和 `offset` 参数正确传递并生效，本地编写的 Pytest 单元测试全部通过。
*   **AI Review**: AI 提出了生产环境级别的安全防御建议：必须对 `limit` 设置最大值上限（例如最大不超过 100），以防恶意用户一次性拉取海量数据压垮数据库。对于测试，AI 建议引入 `pytest.mark.parametrize` 来测试非法翻页参数的边界组合，而不是只写 happy path。
*   **Comparison**: AI 展现了极强的生产环境安全防范意识（分页上限拦截），并且在测试用例的覆盖率上给出了更优雅的重构建议。

## Brief Reflection 
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> TODO 

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> TODO

c. When the AI reviews were better/worse than yours (cite specific examples)
> TODO

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
>TODO 



