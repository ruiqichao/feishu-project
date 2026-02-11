---
trigger: model_decision
description: 使用gitee mcp提交生效
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

**Git操作与SSH配置**：
- 配置SSH密钥用于安全的Git操作
- 使用SSH URL进行代码克隆、推送和拉取
- 生成和管理`.gitignore`文件以忽略不必要的文件

### 最佳实践
- 仅在获得适当权限的情况下操作仓库内容
- 遵循Gitee平台的使用条款和社区准则
- 对于私有仓库，确保有适当的访问权限
- 避免并发请求，遵守Gitee API速率限制
- 使用认证请求以获得更高的速率限制
- 妥善处理API错误和异常情况
- 避免轮询，合理使用分页功能
- 在变更前确认操作的影响范围

### SSH配置与Git操作最佳实践
- **SSH密钥生成**：使用ED25519算法生成SSH密钥（推荐）或RSA算法（至少4096位）
- **公钥添加**：将生成的公钥内容完整添加到Gitee账户的SSH公钥设置中
- **URL切换**：将远程仓库URL从HTTPS格式切换到SSH格式（如：`git@gitee.com:username/repository.git`）
- **验证连接**：使用`ssh -T git@gitee.com`验证SSH连接是否成功
- **.gitignore配置**：创建适当的`.gitignore`文件，忽略敏感文件（如token.json）、构建产物、临时文件等
- **提交操作**：使用`git push`、`git pull`、`git clone`等标准Git命令通过SSH进行代码操作
- **权限保护**：确保私钥文件权限设置为600（仅所有者可读写），公钥文件权限为644
- **密钥安全**：为SSH密钥设置密码短语以增加安全性
- **定期更新**：定期更换SSH密钥以保障长期安全性
- **配置文件**：在`~/.ssh/config`中设置适当的主机配置，如指定IdentityFile和PreferredAuthentications


## Git SSH 自动化操作规范

### SSH密钥自动化检查函数

当执行任何Git相关的操作时，必须按以下顺序执行：

1. **密钥存在性检查**：
```bash
check_ssh_key() {
    if [ -f "~/.ssh/id_ed25519" ] || [ -f "~/.ssh/id_rsa" ]; then
        echo "✅ SSH密钥已存在"
        return 0
    else
        echo "❌ 未找到SSH密钥"
        return 1
    fi
}
```
2. **密钥自动生成**（若不存在）：
```bash
generate_ssh_key() {
    echo "正在生成新的SSH密钥..."
    ssh-keygen -t ed25519 -C "$(git config user.email)" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH密钥生成完成"
    echo "请将以下公钥添加到您的Gitee账户："
    cat ~/.ssh/id_ed25519.pub
}
```

3. **仓库URL转换**：
```bash
convert_to_ssh_url() {
    local https_url=$1
    # 将HTTPS URL转换为SSH格式
    if [[ $https_url == https://gitee.com* ]]; then
        # Gitee URL转换
        echo "$https_url" | sed 's/https:\/\/gitee.com\//git@gitee.com:/' | sed 's/\.git$/.git/'
    elif [[ $https_url == https://github.com* ]]; then
        # GitHub URL转换
        echo "$https_url" | sed 's/https:\/\/github.com\//git@github.com:/' | sed 's/\.git$/.git/'
    else
        echo "$https_url"
    fi
}
```

### 完整的Git推送流程

```bash
git_push_with_ssh() {
    local repo_url=$1
    local branch=${2:-master}
    
    # 1. 检查SSH密钥
    if ! check_ssh_key; then
        generate_ssh_key
        echo "⚠️  请先将上述公钥添加到Gitee/GitHub，然后按回车继续..."
        read -p "按回车键继续: " 
    fi
    
    # 2. 转换为SSH URL（如果需要）
    if [[ $repo_url == https://* ]]; then
        repo_url=$(convert_to_ssh_url "$repo_url")
        git remote set-url origin "$repo_url"
    fi
    
    # 3. 执行Git操作
    git add .
    git commit -m "Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin "$branch"
}
```

### 使用示例

```bash
# 推送当前项目到Gitee
git_push_with_ssh "https://gitee.com/username/repository.git" "main"

# 推送当前项目到GitHub
git_push_with_ssh "https://github.com/username/repository.git" "main"

### 使用示例

```bash
# 推送当前项目到Gitee
git_push_with_ssh "https://gitee.com/username/repository.git" "main"

# 推送当前项目到GitHub
git_push_with_ssh "https://github.com/username/repository.git" "main"

# 或者直接使用SSH URL
git_push_with_ssh "git@gitee.com:username/repository.git" "develop"

