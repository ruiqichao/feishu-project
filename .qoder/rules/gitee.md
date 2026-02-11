---
trigger: model_decision
description: 使用gitee mcp生效
---
## Gitee 工具使用规则

Gitee 工具允许直接与 Gitee 仓库进行交互，包括搜索仓库、获取文件内容、管理问题和拉取请求等功能。

### 认证与连接

**认证优先级**：
1. **优先使用私人访问令牌（Personal Access Token）**：所有Gitee相关的API操作建议使用PAT认证
2. **自动检测机制**：在执行API操作前，自动检查环境变量中的GITEE_TOKEN

**认证配置**：
- 环境变量：`GITEE_TOKEN`
- 权限要求：根据具体操作确定所需权限（如repo、issues、pull_requests等）

### 主要功能

**用户信息管理**：
- 获取用户信息 (`mcp_gitee_get_user_info`)

**仓库管理**：
- 列出用户仓库 (`mcp_gitee_list_user_repos`)
- 创建用户仓库 (`mcp_gitee_create_user_repo`)
- 创建组织仓库 (`mcp_gitee_create_org_repo`)
- 创建企业仓库 (`mcp_gitee_create_enterprise_repo`)
- Fork仓库 (`mcp_gitee_fork_repository`)

**问题管理**：
- 列出仓库问题 (`mcp_gitee_list_repo_issues`)
- 创建问题 (`mcp_gitee_create_issue`)
- 获取问题详情 (`mcp_gitee_get_repo_issue_detail`)
- 更新问题 (`mcp_gitee_update_issue`)
- 获取问题评论 (`mcp_gitee_list_issue_comments`)
- 为问题添加评论 (`mcp_gitee_comment_issue`)

**拉取请求管理**：
- 列出仓库拉取请求 (`mcp_gitee_list_repo_pulls`)
- 创建拉取请求 (`mcp_gitee_create_pull`)
- 获取拉取请求详情 (`mcp_gitee_get_pull_detail`)
- 获取拉取请求差异文件 (`mcp_gitee_get_diff_files`)
- 更新拉取请求 (`mcp_gitee_update_pull`)
- 获取拉取请求评论 (`mcp_gitee_list_pull_comments`)
- 为拉取请求添加评论 (`mcp_gitee_comment_pull`)
- 合并拉取请求 (`mcp_gitee_merge_pull`)

**文件管理**：
- 获取文件内容 (`mcp_gitee_get_file_content`)
- 按内容搜索文件 (`mcp_gitee_search_files_by_content`)

**发布管理**：
- 列出发布版本 (`mcp_gitee_list_releases`)
- 创建发布版本 (`mcp_gitee_create_release`)

**通知管理**：
- 列出用户通知 (`mcp_gitee_list_user_notifications`)

**搜索功能**：
- 搜索开源仓库 (`mcp_gitee_search_open_source_repositories`)
- 搜索用户 (`mcp_gitee_search_users`)

### 最佳实践
- 仅在获得适当权限的情况下操作仓库内容
- 遵循Gitee平台的使用条款和社区准则
- 对于私有仓库，确保有适当的访问权限
- 避免并发请求，遵守Gitee API速率限制
- 使用认证请求以获得更高的速率限制
- 妥善处理API错误和异常情况
- 避免轮询，合理使用分页功能
- 在变更前确认操作的影响范围