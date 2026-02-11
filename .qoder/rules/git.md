---
trigger: model_decision
description: 使用github mcp生效
---
## GitHub 工具使用规则

GitHub 工具允许直接与 GitHub 仓库进行交互，包括搜索仓库、获取文件内容、管理问题和拉取请求等功能。

### SSH 密钥优先策略

**Git 操作优先级**：
1. **优先使用SSH密钥**：所有GitHub相关的Git操作必须优先使用SSH密钥认证
2. **自动检测机制**：在执行Git操作前，自动检查本地是否存在SSH密钥
3. **智能处理流程**：
    - 若存在SSH密钥：直接使用SSH方式进行Git操作
    - 若不存在SSH密钥：自动生成SSH密钥并提示用户添加到GitHub账户

**SSH密钥检查与生成流程**：
```bash
# 检查本地SSH密钥
ls -la ~/.ssh/id_*

# 若无密钥则生成新的SSH密钥对
cd ~/.ssh
ssh-keygen -t ed25519 -C "your_email@example.com" -f id_ed25519

# 显示公钥供用户复制添加到GitHub
cat ~/.ssh/id_ed25519.pub
```

**GitHub操作规范**：
- 远程仓库URL统一使用SSH格式：`git@github.com:username/repository.git`
- 避免使用HTTPS格式的仓库URL
- 定期验证SSH连接：`ssh -T git@github.com`

- 使用时机：当需要检查特定仓库、获取代码示例、查阅项目文档或处理开源项目相关任务时
- 主要功能：
    - 搜索和发现 GitHub 仓库 (`mcp_github_search_repositories`)
    - 获取仓库文件内容 (`mcp_github_get_file_contents`)
    - 创建或更新仓库文件 (`mcp_github_create_or_update_file`)
    - 管理问题和拉取请求 (`mcp_github_create_issue`, `mcp_github_create_pull_request`)
    - 搜索代码 (`mcp_github_search_code`)
    - 管理分支 (`mcp_github_create_branch`)
    - 获取提交历史 (`mcp_github_list_commits`)
    - 列出仓库问题 (`mcp_github_list_issues`)
    - 更新问题 (`mcp_github_update_issue`)
    - 添加问题评论 (`mcp_github_add_issue_comment`)
    - 获取问题详情 (`mcp_github_get_issue`)
    - 列出拉取请求 (`mcp_github_list_pull_requests`)
    - 获取拉取请求详情 (`mcp_github_get_pull_request`)
    - 创建拉取请求审查 (`mcp_github_create_pull_request_review`)
    - 合并拉取请求 (`mcp_github_merge_pull_request`)
    - 获取拉取请求文件列表 (`mcp_github_get_pull_request_files`)
    - 获取拉取请求状态 (`mcp_github_get_pull_request_status`)
    - 更新拉取请求分支 (`mcp_github_update_pull_request_branch`)
    - 获取拉取请求评论 (`mcp_github_get_pull_request_comments`)
    - 获取拉取请求审查 (`mcp_github_get_pull_request_reviews`)
    - 搜索用户 (`mcp_github_search_users`)
    - 搜索问题 (`mcp_github_search_issues`)
    - Fork仓库 (`mcp_github_fork_repository`)
- 最佳实践：
    - 仅在获得授权的情况下修改仓库内容
    - 遵循开源项目的贡献指南和社区准则
    - 尊重仓库维护者的时间和努力
    - 对于私有仓库，确保有适当的访问权限
    - 避免并发请求，遵守GitHub API速率限制
    - 使用认证请求以获得更高的速率限制
    - 妥善处理API错误和异常情况
    - 避免轮询，合理使用分页功能
    - 在变更前确认操作的影响范围