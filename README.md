# 文件完整性监控工具 (File Integrity Monitor)

一个用Python编写的文件完整性监控工具，用于创建文件哈希基线并检测文件更改。

## 功能特性

- 递归扫描目录并计算所有文件的SHA-256哈希值
- 生成JSON格式的基线文件
- 比较当前文件状态与基线，检测更改
- 支持排除特定文件/目录模式
- 多种输出格式：详细报告、JSON格式、安静模式
- 跨平台支持（Windows、Linux、macOS）

## 系统要求

- Python 3.6 或更高版本
- 不需要额外依赖包

## 使用方法

### 创建基线文件

```bash
python fim_tool.py create <目录路径> -o <基线文件>
```

示例：
```bash
python fim_tool.py create /path/to/directory -o baseline.json
```

### 比较文件状态

```bash
python fim_tool.py compare <目录路径> -b <基线文件>
```

示例：
```bash
python fim_tool.py compare /path/to/directory -b baseline.json
```

### 排除特定文件

使用 `-e` 参数排除匹配特定模式的文件：

```bash
python fim_tool.py create /path/to/directory -o baseline.json -e "*.tmp" -e "*.log"
python fim_tool.py compare /path/to/directory -b baseline.json -e "*.tmp" -e "*.log"
```

### 输出选项

- `--json`：输出JSON格式的结果
- `--quiet`：安静模式，只显示摘要
- `--quiet --json`：只输出JSON结果，不显示进度信息

## 基线文件格式

基线文件是JSON格式，包含以下信息：

```json
{
  "directory": "监控目录的绝对路径",
  "created_at": "创建时间戳",
  "created_date": "创建日期时间",
  "total_files": "文件总数",
  "files": {
    "文件路径1": {
      "hash": "SHA-256哈希值",
      "size": "文件大小（字节）",
      "modified_time": "修改时间戳",
      "created_time": "创建时间戳",
      "mode": "文件模式"
    },
    // ... 更多文件
  }
}
```

## 比较结果

比较结果会显示以下信息：

- **修改的文件**：哈希值发生变化的文件
- **新增的文件**：基线中不存在的文件
- **删除的文件**：基线中存在但当前不存在的文件

### 输出示例

```
============================================================
文件完整性监控报告
============================================================
基线文件数: 10
当前文件数: 12
比较时间: 2026-03-16 15:30:51
------------------------------------------------------------

修改的文件 (1 个):
  - file1.txt

新增的文件 (2 个):
  + newfile1.txt
  + newfile2.txt

删除的文件 (1 个):
  x oldfile.txt

------------------------------------------------------------
⚠️  检测到 4 处更改
============================================================
```

## 应用场景

这个文件完整性监控工具在多个领域都有实际应用价值：

### 🔒 安全监控

#### 1. 入侵检测
- **Web服务器文件监控**：检测网站文件是否被篡改（如注入恶意代码）
- **系统关键文件监控**：监控 `/etc/passwd`, `/etc/shadow`, `/etc/sudoers` 等敏感文件
- **Rootkit检测**：检测系统二进制文件是否被替换

```bash
# Web服务器监控示例
python fim_tool.py create /var/www/html -o web_baseline.json -e "*.log" -e "cache/*"
# 通过cron定期检查
0 2 * * * python fim_tool.py compare /var/www/html -b web_baseline.json > /var/log/web_integrity.log
```

#### 2. 恶意软件检测
- 监控系统目录，检测可疑文件的创建和修改
- 结合病毒扫描，提供额外的防护层

### 🖥️ 运维与系统管理

#### 1. 配置管理
- 监控系统配置文件，确保配置不被意外修改
- 跟踪配置变更历史

```bash
# 系统配置监控
python fim_tool.py create /etc -o etc_baseline.json -e "*.swp" -e "*~"
python fim_tool.py compare /etc -b etc_baseline.json -e "*.swp" -e "*~" --json > changes.json
```

#### 2. 变更审计
- 跟踪文件系统变更：谁在何时修改了什么文件
- 变更合规性：确保只有授权人员能修改特定文件

#### 3. 备份验证
- 验证备份文件的完整性
- 确保备份过程中文件没有损坏

### 💻 开发与部署

#### 1. 代码库监控
- 监控源代码目录，检测未经授权的代码修改
- 作为版本控制系统的补充，监控整个工作区

#### 2. 部署验证
- 验证部署完整性：确保部署过程中文件传输正确
- 容器镜像监控：监控容器内文件的变化

```bash
# 容器配置监控
python fim_tool.py create /etc/docker -o docker_config_baseline.json
# 容器重启后验证配置
python fim_tool.py compare /etc/docker -b docker_config_baseline.json
```

#### 3. CI/CD管道
- 在构建前后检查文件完整性
- 确保构建产物没有被意外修改

### 📊 合规与审计

#### 1. PCI DSS合规
- 要求6.3.2：建立检测非授权更改的流程
- 此工具可以作为合规要求的一部分

#### 2. ISO 27001
- A.12.5.1：实施控制措施以保护系统文件的完整性

#### 3. 内部审计
- 定期检查关键系统的文件完整性
- 生成审计报告

### 📁 个人与小型团队

#### 1. 个人项目监控
- 监控重要文档、照片库的完整性
- 检测文件是否被损坏或意外修改

#### 2. 共享文件夹监控
- 监控团队共享目录的文件变化
- 跟踪协作过程中的文件修改

#### 3. 自动化脚本集成
```bash
# 开发环境完整性检查
python fim_tool.py compare ~/project -b ~/project_baseline.json --quiet
# 返回值可用于自动化脚本：有更改输出1，无更改输出0
```

### 🔄 与其他工具对比

| 特性 | 这个工具 | Tripwire/AIDE等专业工具 |
|------|----------|------------------------|
| 轻量级 | ✅ 单文件，无依赖 | ❌ 需要安装配置 |
| 学习成本 | ✅ 简单易懂 | ❌ 配置复杂 |
| 功能丰富度 | ⚠️ 基础功能 | ✅ 企业级功能 |
| 告警机制 | ⚠️ 需自行集成 | ✅ 内置告警 |
| 成本 | ✅ 免费 | ⚠️ 商业版需付费 |

### 🎯 适用场景总结

1. **快速验证**：需要快速检查一组文件是否被修改
2. **资源受限环境**：服务器资源有限，需要轻量级解决方案
3. **临时监控**：短期项目或临时需要监控文件完整性
4. **教育和学习**：理解文件完整性监控的基本原理
5. **小型项目**：个人项目或小团队，不需要复杂的企业级工具
6. **应急响应**：怀疑系统被入侵时，快速检查关键文件

## 注意事项

1. **文件权限**：需要读取权限才能计算文件哈希值
2. **符号链接**：脚本会跟随符号链接读取实际文件内容
3. **大文件处理**：使用分块读取，可以处理大文件
4. **排除模式**：使用标准的glob模式匹配
5. **时间比较**：主要依赖哈希值比较，时间戳仅作为参考信息
6. **目录移动**：如果监控目录被移动，基线中的绝对路径可能不匹配

## 故障排除

### 常见错误

1. **目录不存在**：确保指定的目录路径正确
2. **权限错误**：确保有读取目录和文件的权限
3. **JSON解析错误**：基线文件可能损坏，重新创建基线
4. **路径不匹配**：基线目录与当前目录不匹配时会出现警告

### 调试模式

目前没有专门的调试模式，但可以通过查看错误信息来诊断问题。

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

MIT License 是一个宽松的开源许可证，允许用户自由使用、修改、分发本软件，包括用于商业用途。唯一的限制是在分发时必须包含原始版权声明和许可证文本。

## 贡献

欢迎贡献代码、报告问题或提出改进建议！

### 如何贡献

1. **报告问题**
   - 在GitHub Issues中描述你遇到的问题
   - 提供复现步骤、预期行为和实际行为
   - 如果是错误，请提供相关日志或错误信息

2. **提交功能请求**
   - 描述你想要的功能和使用场景
   - 说明为什么这个功能对项目有价值

3. **提交代码更改**
   - Fork项目到你的账户
   - 创建功能分支 (`git checkout -b feature/amazing-feature`)
   - 提交更改 (`git commit -m 'Add some amazing feature'`)
   - 推送到分支 (`git push origin feature/amazing-feature`)
   - 打开Pull Request

### 开发指南

- 遵循现有的代码风格
- 添加适当的注释和文档
- 确保代码通过基本测试
- 更新README.md以反映重大更改

### 行为准则

请保持专业和尊重的沟通态度。我们致力于为所有人提供一个友好、包容的贡献环境。

## 发布到GitHub

如果你想将这个项目发布到GitHub，可以按照以下步骤操作：

### 1. 创建GitHub仓库
1. 登录GitHub
2. 点击右上角的 "+" 图标，选择 "New repository"
3. 输入仓库名称（如 `file-integrity-monitor`）
4. 添加描述（可选）
5. 选择公开或私有
6. **不要**初始化README、.gitignore或许可证文件（我们已经有了）
7. 点击 "Create repository"

### 2. 初始化本地仓库
```bash
# 进入项目目录
cd /path/to/file_integrity_monitor_FIM

# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: File Integrity Monitor tool"
```

### 3. 连接到远程仓库并推送
```bash
# 添加远程仓库（将REPO_NAME替换为你的仓库名，例如file-integrity-monitor，用户名已设置为aishangwuji）
git remote add origin https://github.com/aishangwuji/REPO_NAME.git

# 推送到GitHub
git push -u origin main
```

### 4. 设置项目信息（可选）
- 在仓库设置中添加项目描述
- 设置主题标签（如 `python`, `security`, `monitoring`, `file-integrity`）
- 添加项目到GitHub Pages（如果需要）

### 5. 后续维护
- 定期更新代码和文档
- 响应Issues和Pull Requests
- 考虑添加CI/CD流程（如GitHub Actions进行自动测试）
