# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
Manual Review (人工审查): 主要检查了 DELETE 接口是否能正确拦截不存在的笔记（返回 404），并确认了 Pydantic 模型加入了字符串非空验证。

AI Review (AI 审查): AI 建议 DELETE 操作成功后严格返回 HTTP 204 No Content，而不是 200 附带 JSON。此外，AI 建议对所有涉及 DB 的操作包裹 SQLAlchemyError 的异常捕获，抛出 500 错误以防止底层结构泄露。

Comparison (对比反思): AI 比人工审查更关注严格的 RESTful 语义规范，并且在异常处理的兜底逻辑上考虑得更全面。

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> TODO

b. PR Description
> TODO

c. Graphite Diamond generated code review
> TODO

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> TODO

b. PR Description
> TODO

c. Graphite Diamond generated code review
> TODO

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> TODO

b. PR Description
> TODO

c. Graphite Diamond generated code review
> TODO

## Brief Reflection 
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> TODO 

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> TODO

c. When the AI reviews were better/worse than yours (cite specific examples)
> TODO

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
>TODO 



