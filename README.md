# 文件完整性监控工具 (File Integrity Monitor)

一个用Python编写的轻量级文件完整性监控工具，用于创建文件哈希基线并检测文件更改。适用于安全监控、系统审计、配置管理等场景。

## 功能特性

- **递归扫描**：自动扫描目录及所有子目录
- **SHA-256哈希**：使用安全的SHA-256算法计算文件哈希值
- **JSON基线文件**：生成结构化的JSON格式基线文件
- **智能比较**：检测文件修改、新增、删除三种变更类型
- **排除模式**：支持glob模式排除特定文件/目录
- **多种输出格式**：
  - 详细报告：完整的变更报告
  - JSON格式：机器可读的输出
  - 安静模式：仅显示摘要
- **跨平台支持**：Windows、Linux、macOS全平台兼容
- **大文件优化**：分块读取，支持超大文件处理
- **错误恢复**：跳过无法访问的文件，继续执行

## 应用场景

### 🔒 安全监控
- **入侵检测**：监控Web服务器文件，检测恶意代码注入
- **系统完整性**：监控`/etc/passwd`、`/etc/shadow`等关键系统文件
- **Rootkit检测**：检测系统二进制文件是否被替换

### 🖥️ 运维管理
- **配置管理**：确保系统配置文件不被意外修改
- **变更审计**：跟踪文件系统变更历史
- **备份验证**：验证备份文件的完整性

### 💻 开发部署
- **代码库监控**：作为版本控制的补充，监控整个工作区
- **部署验证**：确保部署过程中文件传输正确
- **CI/CD集成**：在构建流程中加入完整性检查

### 📊 合规审计
- **PCI DSS合规**：满足6.3.2要求的非授权更改检测
- **ISO 27001**：实施A.12.5.1文件完整性控制
- **内部审计**：定期生成文件完整性审计报告

### 📁 个人与团队
- **个人项目**：监控重要文档、照片库的完整性
- **共享文件夹**：跟踪团队协作中的文件变更
- **自动化集成**：集成到脚本和工作流中

## 安装要求

### 系统要求
- **Python版本**：Python 3.6 或更高版本
- **操作系统**：Windows、Linux、macOS 均可运行
- **依赖包**：无需额外依赖，仅使用Python标准库

### 安装方法
1. 下载项目文件：
   ```bash
   git clone https://github.com/aishangwuji/file-integrity-monitor.git
   cd file-integrity-monitor
   ```

2. 验证Python环境：
   ```bash
   python --version  # 或 python3 --version
   ```

3. 工具可直接使用，无需安装：
   ```bash
   python fim_tool.py --help
   ```

## 快速开始

### 1. 创建基线文件
```bash
# 扫描目录并创建基线
python fim_tool.py create /path/to/directory -o baseline.json
```

### 2. 检测文件变更
```bash
# 比较当前状态与基线
python fim_tool.py compare /path/to/directory -b baseline.json
```

### 3. 简单监控示例
```bash
# 监控网站目录（排除日志和缓存文件）
python fim_tool.py create /var/www/html -o web_baseline.json -e "*.log" -e "cache/*"

# 定期检查（通过cron）
0 2 * * * python fim_tool.py compare /var/www/html -b web_baseline.json --quiet
```

## 使用方法

### 创建基线文件
```bash
python fim_tool.py create <目录路径> [选项]
```

**选项**：
- `-o, --output <文件>`：基线输出文件路径（默认：baseline.json）
- `-e, --exclude <模式>`：排除文件/目录模式（可多次使用）
- `--help`：显示帮助信息

**示例**：
```bash
# 创建基线，排除临时文件和日志
python fim_tool.py create /etc -o etc_baseline.json -e "*.tmp" -e "*.log" -e "*.swp"
```

### 比较文件状态
```bash
python fim_tool.py compare <目录路径> [选项]
```

**选项**：
- `-b, --baseline <文件>`：基线文件路径（默认：baseline.json）
- `-e, --exclude <模式>`：排除文件/目录模式（可多次使用）
- `--json`：输出JSON格式结果
- `--quiet`：安静模式，仅显示摘要
- `--help`：显示帮助信息

**示例**：
```bash
# 详细报告模式
python fim_tool.py compare /etc -b etc_baseline.json

# JSON输出模式
python fim_tool.py compare /etc -b etc_baseline.json --json > changes.json

# 安静模式（适合脚本集成）
python fim_tool.py compare /etc -b etc_baseline.json --quiet
```

## 检测规则

### 1. 哈希值比较
工具通过比较文件的SHA-256哈希值来检测变更：
- **相同哈希值**：文件未修改
- **不同哈希值**：文件内容已修改

### 2. 文件存在性检查
- **基线中存在，当前不存在**：文件被删除
- **基线中不存在，当前存在**：新增文件

### 3. 变更类型定义
- **修改的文件**：哈希值发生变化（文件内容被更改）
- **新增的文件**：基线中不存在的新文件
- **删除的文件**：基线中存在但当前已删除的文件

### 4. 排除规则
使用glob模式匹配排除特定文件：
- `*.tmp`：排除所有.tmp文件
- `logs/*`：排除logs目录下所有文件
- `temp/`：排除temp目录

## 报告内容

### 详细报告格式
```
============================================================
文件完整性监控报告
============================================================
基线文件数: 10
当前文件数: 12
比较时间: 2026-03-16 15:30:51
------------------------------------------------------------

修改的文件 (2 个):
  - /etc/nginx/nginx.conf
  - /etc/ssh/sshd_config

新增的文件 (3 个):
  + /etc/new_config.yaml
  + /etc/scripts/backup.sh
  + /var/log/audit.log

删除的文件 (1 个):
  x /etc/old_config.conf

------------------------------------------------------------
⚠️  检测到 6 处更改
============================================================
```

### 报告字段说明
- **基线文件数**：基线文件中记录的文件总数
- **当前文件数**：当前目录扫描到的文件总数
- **比较时间**：执行比较的时间戳
- **修改的文件**：哈希值发生变化的文件列表
- **新增的文件**：基线中不存在的新文件列表
- **删除的文件**：基线中存在但当前已删除的文件列表

## 日志格式支持

### 1. 详细报告模式（默认）
- 完整的格式化报告
- 适合人工查看和分析
- 包含颜色编码和分隔符

### 2. JSON格式（`--json`参数）
- 机器可读的结构化数据
- 适合集成到其他系统
- 包含完整变更信息

```json
{
  "changed": ["file1.txt", "file2.conf"],
  "new": ["newfile.txt"],
  "deleted": ["oldfile.txt"],
  "total_current": 15,
  "total_baseline": 14,
  "comparison_time": "2026-03-16 15:30:51"
}
```

### 3. 安静模式（`--quiet`参数）
- 仅显示摘要信息
- 适合脚本集成和自动化
- 退出代码：0=无更改，非0=有更改

### 4. 组合模式
- `--quiet --json`：仅输出JSON，无进度信息
- 适合完全自动化场景

## 测试与示例

### 基础测试
```bash
# 创建测试目录
mkdir -p test_dir
echo "Test file 1" > test_dir/file1.txt
echo "Test file 2" > test_dir/file2.txt

# 创建基线
python fim_tool.py create test_dir -o test_baseline.json

# 验证无更改
python fim_tool.py compare test_dir -b test_baseline.json --quiet
# 输出：未检测到更改
```

### 变更检测测试
```bash
# 修改文件
echo "Modified content" > test_dir/file1.txt

# 删除文件
rm test_dir/file2.txt

# 创建新文件
echo "New file" > test_dir/file3.txt

# 检测变更
python fim_tool.py compare test_dir -b test_baseline.json
# 将显示：1个修改、1个删除、1个新增
```

### 排除模式测试
```bash
# 创建包含临时文件的目录
echo "Keep me" > test_dir/important.txt
echo "Exclude me" > test_dir/temp.tmp

# 创建基线（排除.tmp文件）
python fim_tool.py create test_dir -o test_baseline.json -e "*.tmp"

# 修改临时文件（不会被检测）
echo "Changed temp" > test_dir/temp.tmp

# 检查（临时文件变更不会被报告）
python fim_tool.py compare test_dir -b test_baseline.json -e "*.tmp"
```

## 输出文件

### 基线文件格式
基线文件是JSON格式，包含以下字段：

```json
{
  "directory": "监控目录的绝对路径",
  "created_at": 1773646209.9097233,
  "created_date": "2026-03-16 15:30:09",
  "total_files": 42,
  "files": {
    "relative/path/to/file1.txt": {
      "hash": "d6746a5ef409f28e6609f6d14e947c3e51db6c6a0cc7a9fc275db8b9c7637ba8",
      "size": 1024,
      "modified_time": 1773646079.5901878,
      "created_time": 1773646079.5901878,
      "mode": 33206
    },
    "relative/path/to/file2.conf": {
      "hash": "52f41eed67f78aae8c544da6bc1ed960d066e791f38b77f7e76dbc8b77b0c986",
      "size": 2048,
      "modified_time": 1773646079.5901878,
      "created_time": 1773646079.5901878,
      "mode": 33206
    }
  }
}
```

### 字段说明
- **directory**：监控目录的绝对路径
- **created_at**：基线创建时间戳（Unix时间戳）
- **created_date**：基线创建时间（可读格式）
- **total_files**：基线中包含的文件总数
- **files**：文件信息字典，键为相对路径
  - **hash**：文件的SHA-256哈希值
  - **size**：文件大小（字节）
  - **modified_time**：最后修改时间戳
  - **created_time**：创建时间戳（如果系统支持）
  - **mode**：文件权限模式

## 注意事项

### 1. 权限要求
- **读取权限**：需要读取目录和文件的权限才能计算哈希值
- **符号链接**：工具会跟随符号链接读取实际文件内容
- **特殊文件**：设备文件、管道等特殊文件可能无法处理

### 2. 性能考虑
- **大文件处理**：使用分块读取，但仍可能消耗较多I/O
- **目录大小**：包含大量文件的目录可能需要较长时间扫描
- **内存使用**：基线文件会完全加载到内存中

### 3. 路径处理
- **绝对路径**：基线中存储绝对路径，目录移动可能导致路径不匹配
- **相对路径**：文件路径以相对于监控目录的形式存储
- **路径分隔符**：Windows使用`\`，Unix使用`/`，工具会自动处理

### 4. 哈希算法
- **SHA-256**：使用标准SHA-256算法，抗碰撞性强
- **哈希冲突**：理论上可能但实际概率极低
- **文件内容**：仅哈希文件内容，不包含文件名或路径

### 5. 时间戳
- **修改时间**：仅作为参考，主要依赖哈希值比较
- **时区**：所有时间戳使用系统本地时区
- **精度**：时间戳精确到秒

## 扩展建议

### 1. 监控功能扩展
- **实时监控**：添加inotify/fsevents支持，实时检测文件变更
- **计划任务**：集成定时任务，定期自动检查
- **通知机制**：支持邮件、Slack、Webhook等通知方式

### 2. 安全增强
- **基线加密**：支持加密存储基线文件
- **数字签名**：为基线文件添加数字签名
- **完整性验证**：验证基线文件本身的完整性

### 3. 性能优化
- **增量扫描**：只扫描发生变化的文件
- **并行处理**：多线程/多进程加速文件哈希计算
- **缓存机制**：缓存文件哈希值，减少重复计算

### 4. 集成扩展
- **API接口**：提供REST API供其他系统调用
- **插件系统**：支持自定义检测规则和输出格式
- **配置管理**：支持配置文件管理监控任务

### 5. 报告增强
- **历史记录**：保存变更历史，支持时间线查看
- **可视化报告**：生成HTML或PDF格式的图形化报告
- **统计分析**：提供变更统计和趋势分析

## 故障排除

### 常见错误
1. **目录不存在**
   ```
   错误: 目录不存在或不是目录: /path/to/nonexistent
   ```
   **解决方案**：检查目录路径是否正确

2. **权限错误**
   ```
   警告: 跳过文件 /path/to/file: [Errno 13] Permission denied
   ```
   **解决方案**：确保有读取权限，或使用排除模式跳过

3. **JSON解析错误**
   ```
   错误: 无法读取基线文件: Expecting value: line 1 column 1 (char 0)
   ```
   **解决方案**：基线文件可能损坏，重新创建基线

4. **路径不匹配**
   ```
   警告: 基线目录 (/old/path) 与当前目录 (/new/path) 不匹配
   ```
   **解决方案**：重新创建基线，或手动修改基线文件中的路径

### 调试技巧
- 使用 `--verbose` 参数获取更多信息（如果支持）
- 检查Python错误堆栈
- 验证文件权限和路径
- 测试小范围目录确认功能正常

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

**MIT许可证要点**：
- 允许自由使用、复制、修改、合并、出版发行、散布、再授权及售卖软件副本
- 唯一要求：在软件和软件的所有副本中包含版权声明和许可声明
- 软件按"原样"提供，不承担任何明示或暗示的担保责任

**完整许可证文本请查看 [LICENSE](LICENSE) 文件。**

## 贡献

欢迎贡献代码、报告问题或提出改进建议！

### 如何贡献

1. **报告问题**
   - 在GitHub Issues中描述遇到的问题
   - 提供复现步骤、预期行为和实际行为
   - 如果是错误，请提供相关日志或错误信息

2. **提交功能请求**
   - 描述想要的功能和使用场景
   - 说明为什么这个功能对项目有价值
   - 讨论实现方案和潜在影响

3. **提交代码更改**
   - Fork项目到你的账户
   - 创建功能分支 (`git checkout -b feature/amazing-feature`)
   - 提交更改 (`git commit -m 'Add some amazing feature'`)
   - 推送到分支 (`git push origin feature/amazing-feature`)
   - 打开Pull Request

### 开发指南
- 遵循现有的代码风格和命名约定
- 添加适当的注释和文档
- 确保代码通过基本测试
- 更新README.md以反映重大更改

### 行为准则
请保持专业和尊重的沟通态度。我们致力于为所有人提供一个友好、包容的贡献环境。

---

## 相关资源
- [GitHub仓库](https://github.com/aishangwuji/file-integrity-monitor)
- [问题跟踪](https://github.com/aishangwuji/file-integrity-monitor/issues)
- [发布版本](https://github.com/aishangwuji/file-integrity-monitor/releases)

## 更新日志
- **v1.0.0** (2026-03-16): 初始版本发布，包含基线创建和变更检测功能

---

**项目维护者**: [aishangwuji](https://github.com/aishangwuji)