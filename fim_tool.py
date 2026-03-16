#!/usr/bin/env python3
"""
文件完整性监控工具 (File Integrity Monitor)
用于创建文件哈希基线并检测文件更改。
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import time


def calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """计算文件的SHA-256哈希值

    Args:
        file_path: 文件路径
        chunk_size: 读取块大小

    Returns:
        SHA-256哈希值的十六进制字符串
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # 分块读取文件以避免内存问题
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except (IOError, OSError) as e:
        print(f"警告: 无法读取文件 {file_path}: {e}", file=sys.stderr)
        raise


def scan_directory(directory: Path, exclude_patterns: Optional[List[str]] = None) -> Dict[str, dict]:
    """扫描目录并收集文件信息

    Args:
        directory: 要扫描的目录路径
        exclude_patterns: 要排除的文件/目录模式列表

    Returns:
        字典，键为文件路径（相对路径），值为包含文件信息的字典
    """
    if exclude_patterns is None:
        exclude_patterns = []

    file_data = {}
    directory_str = str(directory.resolve())

    for root, dirs, files in os.walk(directory):
        # 应用排除模式
        for pattern in exclude_patterns:
            dirs[:] = [d for d in dirs if not Path(os.path.join(root, d)).match(pattern)]
            files[:] = [f for f in files if not Path(os.path.join(root, f)).match(pattern)]

        for file in files:
            file_path = Path(root) / file
            try:
                # 获取相对路径
                rel_path = str(file_path.relative_to(directory))

                # 获取文件统计信息
                stat = file_path.stat()

                # 计算哈希值
                file_hash = calculate_file_hash(file_path)

                file_data[rel_path] = {
                    'hash': file_hash,
                    'size': stat.st_size,
                    'modified_time': stat.st_mtime,
                    'created_time': stat.st_ctime if hasattr(stat, 'st_ctime') else None,
                    'mode': stat.st_mode
                }
            except (IOError, OSError, ValueError) as e:
                print(f"警告: 跳过文件 {file_path}: {e}", file=sys.stderr)
                continue

    return file_data


def create_baseline(directory: Path, output_file: Path, exclude_patterns: Optional[List[str]] = None) -> None:
    """创建基线文件

    Args:
        directory: 要监控的目录
        output_file: 基线输出文件路径
        exclude_patterns: 要排除的文件/目录模式列表
    """
    if not directory.exists() or not directory.is_dir():
        print(f"错误: 目录不存在或不是目录: {directory}", file=sys.stderr)
        sys.exit(1)

    print(f"正在扫描目录: {directory}")
    print(f"输出基线文件: {output_file}")

    # 扫描目录
    file_data = scan_directory(directory, exclude_patterns)

    # 创建基线数据结构
    baseline = {
        'directory': str(directory.resolve()),
        'created_at': time.time(),
        'created_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': len(file_data),
        'files': file_data
    }

    # 保存为JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        print(f"基线文件创建成功，共扫描 {len(file_data)} 个文件")
    except (IOError, OSError) as e:
        print(f"错误: 无法写入基线文件: {e}", file=sys.stderr)
        sys.exit(1)


def compare_with_baseline(directory: Path, baseline_file: Path, exclude_patterns: Optional[List[str]] = None, verbose: bool = True) -> Dict[str, List[str]]:
    """比较当前目录状态与基线

    Args:
        directory: 要监控的目录
        baseline_file: 基线文件路径
        exclude_patterns: 要排除的文件/目录模式列表
        verbose: 是否显示进度信息

    Returns:
        包含变更信息的字典
    """
    if verbose:
        print(f"正在比较目录: {directory}")
        print(f"使用基线文件: {baseline_file}")

    # 加载基线数据
    try:
        with open(baseline_file, 'r', encoding='utf-8') as f:
            baseline = json.load(f)
    except (IOError, OSError, json.JSONDecodeError) as e:
        print(f"错误: 无法读取基线文件: {e}", file=sys.stderr)
        sys.exit(1)

    # 验证基线目录是否匹配
    baseline_dir = Path(baseline.get('directory', ''))
    if baseline_dir.resolve() != directory.resolve():
        print(f"警告: 基线目录 ({baseline_dir}) 与当前目录 ({directory}) 不匹配")
        print("继续比较，但结果可能不准确")

    # 扫描当前目录
    current_files = scan_directory(directory, exclude_patterns)

    # 获取基线中的文件
    baseline_files = baseline.get('files', {})

    # 比较文件
    changed_files = []
    new_files = []
    deleted_files = []

    # 检查修改的文件
    for file_path, current_info in current_files.items():
        if file_path in baseline_files:
            baseline_info = baseline_files[file_path]
            if current_info['hash'] != baseline_info.get('hash'):
                changed_files.append(file_path)

    # 检查新增的文件
    new_files = [f for f in current_files.keys() if f not in baseline_files]

    # 检查删除的文件
    deleted_files = [f for f in baseline_files.keys() if f not in current_files]

    # 准备结果
    result = {
        'changed': changed_files,
        'new': new_files,
        'deleted': deleted_files,
        'total_current': len(current_files),
        'total_baseline': len(baseline_files),
        'comparison_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    return result


def print_comparison_result(result: Dict[str, List[str]]) -> None:
    """打印比较结果

    Args:
        result: 比较结果字典
    """
    print("\n" + "="*60)
    print("文件完整性监控报告")
    print("="*60)
    print(f"基线文件数: {result['total_baseline']}")
    print(f"当前文件数: {result['total_current']}")
    print(f"比较时间: {result['comparison_time']}")
    print("-"*60)

    # 打印更改的文件
    if result['changed']:
        print(f"\n修改的文件 ({len(result['changed'])} 个):")
        for file in sorted(result['changed']):
            print(f"  - {file}")
    else:
        print("\n修改的文件: 无")

    # 打印新增的文件
    if result['new']:
        print(f"\n新增的文件 ({len(result['new'])} 个):")
        for file in sorted(result['new']):
            print(f"  + {file}")
    else:
        print("\n新增的文件: 无")

    # 打印删除的文件
    if result['deleted']:
        print(f"\n删除的文件 ({len(result['deleted'])} 个):")
        for file in sorted(result['deleted']):
            print(f"  x {file}")
    else:
        print("\n删除的文件: 无")

    # 总结
    print("\n" + "-"*60)
    total_changes = len(result['changed']) + len(result['new']) + len(result['deleted'])
    if total_changes == 0:
        print("✅ 所有文件完整，未检测到更改")
    else:
        print(f"⚠️  检测到 {total_changes} 处更改")
    print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='文件完整性监控工具 - 创建基线并检测文件更改',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s create /path/to/directory -o baseline.json
  %(prog)s compare /path/to/directory -b baseline.json

排除模式示例:
  %(prog)s create /path/to/directory -o baseline.json -e "*.tmp" -e "*.log"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令', required=True)

    # 创建基线子命令
    create_parser = subparsers.add_parser('create', help='创建基线文件')
    create_parser.add_argument('directory', type=Path, help='要监控的目录')
    create_parser.add_argument('-o', '--output', type=Path, default='baseline.json',
                              help='基线输出文件路径 (默认: baseline.json)')
    create_parser.add_argument('-e', '--exclude', action='append', default=[],
                              help='要排除的文件/目录模式 (可多次使用)')

    # 比较子命令
    compare_parser = subparsers.add_parser('compare', help='比较当前状态与基线')
    compare_parser.add_argument('directory', type=Path, help='要监控的目录')
    compare_parser.add_argument('-b', '--baseline', type=Path, default='baseline.json',
                               help='基线文件路径 (默认: baseline.json)')
    compare_parser.add_argument('-e', '--exclude', action='append', default=[],
                               help='要排除的文件/目录模式 (可多次使用)')
    compare_parser.add_argument('-q', '--quiet', action='store_true',
                               help='安静模式，只输出JSON结果')
    compare_parser.add_argument('-j', '--json', action='store_true',
                               help='输出JSON格式结果')

    args = parser.parse_args()

    try:
        if args.command == 'create':
            create_baseline(args.directory, args.output, args.exclude)

        elif args.command == 'compare':
            result = compare_with_baseline(args.directory, args.baseline, args.exclude, verbose=not args.quiet)

            if args.quiet and args.json:
                # 只输出JSON，没有其他信息
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.json:
                # 输出JSON格式结果
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.quiet:
                # 只输出总结
                total_changes = len(result['changed']) + len(result['new']) + len(result['deleted'])
                if total_changes > 0:
                    print(f"检测到 {total_changes} 处更改")
                else:
                    print("未检测到更改")
            else:
                # 打印详细报告
                print_comparison_result(result)

    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()