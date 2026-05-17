#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiDash 命令行接口
WiFiDash Command Line Interface

提供命令行扫描和诊断功能
Provides command-line scanning and diagnostics
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

from .core.scanner import WiFiScanner


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器 / Create command-line argument parser
    
    Returns:
        argparse.ArgumentParser: 参数解析器 / Argument parser
    """
    parser = argparse.ArgumentParser(
        prog='wifidash',
        description='WiFiDash - 智能WiFi网络诊断工具 / Smart WiFi Network Diagnostics Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 / Examples:
  wifidash                    启动交互式TUI界面 / Launch interactive TUI
  wifidash scan               执行一次扫描并显示结果 / Perform scan and show results
  wifidash scan --json        以JSON格式输出 / Output in JSON format
  wifidash scan --export scan.json   导出到文件 / Export to file
  wifidash channels           分析信道使用情况 / Analyze channel usage
  wifidash recommend          获取优化建议 / Get optimization recommendations
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令 / Available commands')
    
    # scan 命令 / scan command
    scan_parser = subparsers.add_parser('scan', help='扫描WiFi网络 / Scan WiFi networks')
    scan_parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='以JSON格式输出 / Output in JSON format'
    )
    scan_parser.add_argument(
        '--export', '-e',
        metavar='FILE',
        help='导出到文件 / Export to file'
    )
    scan_parser.add_argument(
        '--limit', '-l',
        type=int,
        default=0,
        help='限制显示数量 / Limit number of results'
    )
    
    # channels 命令 / channels command
    channel_parser = subparsers.add_parser('channels', help='分析信道使用情况 / Analyze channel usage')
    channel_parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='以JSON格式输出 / Output in JSON format'
    )
    
    # recommend 命令 / recommend command
    recommend_parser = subparsers.add_parser('recommend', help='获取优化建议 / Get optimization recommendations')
    recommend_parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='以JSON格式输出 / Output in JSON format'
    )
    
    # monitor 命令 / monitor command
    monitor_parser = subparsers.add_parser('monitor', help='持续监控模式 / Continuous monitoring mode')
    monitor_parser.add_argument(
        '--interval', '-i',
        type=int,
        default=5,
        help='扫描间隔(秒) / Scan interval in seconds (default: 5)'
    )
    monitor_parser.add_argument(
        '--duration', '-d',
        type=int,
        default=0,
        help='监控时长(秒), 0为无限 / Monitor duration in seconds, 0 for infinite'
    )
    
    # version
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='WiFiDash 1.0.0'
    )
    
    return parser


def print_scan_results(networks, json_output: bool = False, limit: int = 0):
    """
    打印扫描结果 / Print scan results
    
    Args:
        networks: 网络列表 / Network list
        json_output: 是否JSON输出 / Whether to output as JSON
        limit: 结果限制 / Result limit
    """
    if json_output:
        data = {
            "scan_time": datetime.now().isoformat(),
            "network_count": len(networks),
            "networks": [net.to_dict() for net in networks]
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    
    # 表格输出 / Table output
    print(f"\n{'='*80}")
    print(f"📶 WiFi扫描结果 / WiFi Scan Results ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'='*80}")
    print(f"{'SSID':<25} {'Security':<15} {'Signal':<10} {'Channel':<8} {'Mode':<10}")
    print(f"{'-'*80}")
    
    sorted_networks = sorted(networks, key=lambda x: x.signal_dbm, reverse=True)
    if limit > 0:
        sorted_networks = sorted_networks[:limit]
    
    for net in sorted_networks:
        signal_bar = "█" * (net.quality // 10) + "░" * (10 - net.quality // 10)
        print(f"{net.ssid:<25} {net.security:<15} {net.signal_dbm:>4}dBm {net.channel:<8} {net.mode:<10}")
        print(f"  └─ Quality: {signal_bar} {net.quality}%")
    
    print(f"{'='*80}")
    print(f"总计 / Total: {len(networks)} 个网络 / networks\n")


def print_channel_analysis(channels, json_output: bool = False):
    """
    打印信道分析结果 / Print channel analysis results
    
    Args:
        channels: 信道列表 / Channel list
        json_output: 是否JSON输出 / Whether to output as JSON
    """
    if json_output:
        data = {
            "analysis_time": datetime.now().isoformat(),
            "channels": [
                {
                    "channel": c.channel,
                    "frequency": c.frequency,
                    "usage_count": c.usage_count,
                    "avg_signal": c.avg_signal,
                    "congestion_level": c.congestion_level,
                    "networks": c.networks
                }
                for c in channels
            ]
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    
    print(f"\n{'='*70}")
    print(f"📊 信道使用分析 / Channel Usage Analysis ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'='*70}")
    print(f"{'Channel':<10} {'Freq(GHz)':<12} {'Networks':<10} {'Avg Signal':<12} {'Congestion':<12}")
    print(f"{'-'*70}")
    
    for ch in sorted(channels, key=lambda x: x.channel):
        cong_icon = "🟢" if ch.congestion_level == "Low" else "🟡" if ch.congestion_level == "Medium" else "🔴"
        print(f"{ch.channel:<10} {ch.frequency:<12.3f} {ch.usage_count:<10} {ch.avg_signal:<12.0f} {cong_icon} {ch.congestion_level:<10}")
    
    print(f"{'='*70}\n")


def print_recommendations(recs: dict, json_output: bool = False):
    """
    打印优化建议 / Print optimization recommendations
    
    Args:
        recs: 建议字典 / Recommendations dictionary
        json_output: 是否JSON输出 / Whether to output as JSON
    """
    if json_output:
        print(json.dumps(recs, indent=2, ensure_ascii=False))
        return
    
    print(f"\n{'='*70}")
    print(f"💡 网络优化建议 / Network Optimization Recommendations")
    print(f"{'='*70}")
    
    print("\n🎯 最佳信道推荐 / Best Channel Recommendations:")
    if recs.get('best_24ghz_channel'):
        print(f"  • 2.4GHz: 信道 {recs['best_24ghz_channel']} (推荐 / Recommended)")
    if recs.get('best_5ghz_channel'):
        print(f"  • 5GHz: 信道 {recs['best_5ghz_channel']} (推荐 / Recommended)")
    
    print("\n🔒 安全提醒 / Security Alerts:")
    issues = recs.get('security_issues', [])
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ 未发现明显安全问题 / No obvious security issues found")
    
    print(f"\n📡 信号覆盖分析 / Signal Coverage Analysis:")
    print(f"  • 检测到的网络总数 / Total networks detected: {recs.get('total_networks', 0)}")
    print(f"  • 弱信号网络数量 / Weak signal networks: {recs.get('weak_signal_count', 0)}")
    
    if recs.get('weak_signal_count', 0) > 0:
        print("  💡 建议: 考虑调整路由器位置或使用信号放大器")
        print("     Tip: Consider repositioning your router or using a signal booster")
    
    print(f"{'='*70}\n")


def cmd_scan(args) -> int:
    """
    执行扫描命令 / Execute scan command
    
    Args:
        args: 命令参数 / Command arguments
        
    Returns:
        int: 退出码 / Exit code
    """
    scanner = WiFiScanner()
    print("🔍 正在扫描WiFi网络... / Scanning WiFi networks...")
    
    try:
        networks = scanner.scan()
        print_scan_results(networks, args.json, args.limit)
        
        if args.export:
            scanner.export_to_json(networks, args.export)
            print(f"✓ 结果已导出到 / Results exported to: {args.export}")
        
        return 0
    except Exception as e:
        print(f"✗ 扫描失败 / Scan failed: {e}", file=sys.stderr)
        return 1


def cmd_channels(args) -> int:
    """
    执行信道分析命令 / Execute channel analysis command
    
    Args:
        args: 命令参数 / Command arguments
        
    Returns:
        int: 退出码 / Exit code
    """
    scanner = WiFiScanner()
    print("📊 正在分析信道使用情况... / Analyzing channel usage...")
    
    try:
        networks = scanner.scan()
        channels = scanner.analyze_channels(networks)
        print_channel_analysis(channels, args.json)
        return 0
    except Exception as e:
        print(f"✗ 分析失败 / Analysis failed: {e}", file=sys.stderr)
        return 1


def cmd_recommend(args) -> int:
    """
    执行建议命令 / Execute recommend command
    
    Args:
        args: 命令参数 / Command arguments
        
    Returns:
        int: 退出码 / Exit code
    """
    scanner = WiFiScanner()
    print("💡 正在生成优化建议... / Generating recommendations...")
    
    try:
        networks = scanner.scan()
        recs = scanner.get_recommendations(networks)
        print_recommendations(recs, args.json)
        return 0
    except Exception as e:
        print(f"✗ 建议生成失败 / Recommendation failed: {e}", file=sys.stderr)
        return 1


def cmd_monitor(args) -> int:
    """
    执行监控命令 / Execute monitor command
    
    Args:
        args: 命令参数 / Command arguments
        
    Returns:
        int: 退出码 / Exit code
    """
    scanner = WiFiScanner()
    interval = args.interval
    duration = args.duration
    
    print(f"📡 启动监控模式 (间隔: {interval}秒) / Starting monitor mode (interval: {interval}s)")
    if duration > 0:
        print(f"⏱️  监控时长: {duration}秒 / Monitor duration: {duration}s")
    print("按 Ctrl+C 停止 / Press Ctrl+C to stop\n")
    
    try:
        import time
        start_time = time.time()
        scan_count = 0
        
        while True:
            networks = scanner.scan()
            scan_count += 1
            
            print(f"\n--- 扫描 #{scan_count} / Scan #{scan_count} ({datetime.now().strftime('%H:%M:%S')}) ---")
            print_scan_results(networks, limit=5)
            
            if duration > 0 and (time.time() - start_time) >= duration:
                print("\n✓ 监控完成 / Monitor complete")
                break
            
            time.sleep(interval)
        
        return 0
    except KeyboardInterrupt:
        print("\n\n✓ 监控已停止 / Monitor stopped")
        return 0
    except Exception as e:
        print(f"\n✗ 监控错误 / Monitor error: {e}", file=sys.stderr)
        return 1


def main():
    """CLI主入口 / CLI main entry"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 如果没有命令，启动TUI / If no command, launch TUI
    if not args.command:
        from .ui import main as tui_main
        tui_main()
        return 0
    
    # 执行对应命令 / Execute corresponding command
    commands = {
        'scan': cmd_scan,
        'channels': cmd_channels,
        'recommend': cmd_recommend,
        'monitor': cmd_monitor,
    }
    
    if args.command in commands:
        return commands[args.command](args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
