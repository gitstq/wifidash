#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiDash TUI 应用程序
WiFiDash TUI Application

基于Textual的交互式WiFi网络诊断工具
Interactive WiFi network diagnostics tool based on Textual
"""

import asyncio
from typing import List, Optional
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import (
    Header, Footer, DataTable, Static, Button, 
    ProgressBar, Label, RichLog, TabbedContent, TabPane,
    Input, Select, Switch
)
from textual.reactive import reactive
from textual.binding import Binding
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
from rich.table import Table as RichTable
from rich.syntax import Syntax

from ..core.scanner import WiFiScanner, WiFiNetwork, ChannelInfo


class SignalBar(Static):
    """信号强度条形图组件 / Signal strength bar component"""
    
    def __init__(self, signal: int, **kwargs):
        super().__init__(**kwargs)
        self.signal = signal
    
    def render(self) -> Text:
        """渲染信号条 / Render signal bar"""
        quality = max(0, min(100, self.signal + 100))
        filled = int(quality / 10)
        empty = 10 - filled
        
        if quality >= 80:
            color = "green"
        elif quality >= 60:
            color = "yellow"
        elif quality >= 40:
            color = "orange"
        else:
            color = "red"
        
        bar = "█" * filled + "░" * empty
        return Text(f"{bar} {quality}%", style=color)


class NetworkTable(DataTable):
    """网络列表表格组件 / Network list table component"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
    
    def on_mount(self):
        """组件挂载时初始化 / Initialize on mount"""
        self.add_columns(
            "📶 SSID",
            "🔒 Security",
            "📡 Signal",
            "📊 Quality",
            "📻 Channel",
            "🔧 Mode"
        )
    
    def update_networks(self, networks: List[WiFiNetwork]):
        """更新网络列表 / Update network list"""
        self.clear()
        
        # 按信号强度排序 / Sort by signal strength
        sorted_networks = sorted(networks, key=lambda x: x.signal_dbm, reverse=True)
        
        for net in sorted_networks:
            # 信号强度颜色 / Signal strength color
            if net.signal_dbm >= -50:
                signal_style = "green"
            elif net.signal_dbm >= -65:
                signal_style = "yellow"
            elif net.signal_dbm >= -75:
                signal_style = "orange"
            else:
                signal_style = "red"
            
            # 安全等级图标 / Security level icon
            if net.security == "Open":
                sec_icon = "🔓"
            elif net.security in ["WEP", "WPA"]:
                sec_icon = "⚠️"
            else:
                sec_icon = "🔐"
            
            self.add_row(
                net.ssid,
                f"{sec_icon} {net.security}",
                Text(f"{net.signal_dbm} dBm", style=signal_style),
                Text(f"{net.quality}%", style=signal_style),
                str(net.channel),
                net.mode
            )


class ChannelChart(Static):
    """信道使用图表组件 / Channel usage chart component"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channels: List[ChannelInfo] = []
    
    def update_channels(self, channels: List[ChannelInfo]):
        """更新信道数据 / Update channel data"""
        self.channels = channels
        self.refresh()
    
    def render(self) -> Panel:
        """渲染信道图表 / Render channel chart"""
        if not self.channels:
            return Panel("暂无数据 / No data", title="📊 信道分析 / Channel Analysis")
        
        table = RichTable(show_header=True, header_style="bold cyan")
        table.add_column("Channel", justify="center")
        table.add_column("Freq (GHz)", justify="center")
        table.add_column("Networks", justify="center")
        table.add_column("Avg Signal", justify="center")
        table.add_column("Congestion", justify="center")
        table.add_column("Visual", min_width=20)
        
        for ch in sorted(self.channels, key=lambda x: x.channel):
            # 拥堵等级颜色 / Congestion level color
            if ch.congestion_level == "Low":
                cong_style = "green"
                cong_text = "🟢 Low"
            elif ch.congestion_level == "Medium":
                cong_style = "yellow"
                cong_text = "🟡 Medium"
            else:
                cong_style = "red"
                cong_text = "🔴 High"
            
            # 可视化条形图 / Visual bar chart
            bar_width = min(ch.usage_count * 3, 20)
            bar = "█" * bar_width
            
            table.add_row(
                str(ch.channel),
                f"{ch.frequency:.3f}",
                str(ch.usage_count),
                f"{ch.avg_signal:.0f} dBm",
                Text(cong_text, style=cong_style),
                Text(bar, style=cong_style)
            )
        
        return Panel(table, title="📊 信道分析 / Channel Analysis", border_style="cyan")


class RecommendationsPanel(Static):
    """建议面板组件 / Recommendations panel component"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recommendations = {}
    
    def update_recommendations(self, recs: dict):
        """更新建议内容 / Update recommendations"""
        self.recommendations = recs
        self.refresh()
    
    def render(self) -> Panel:
        """渲染建议面板 / Render recommendations panel"""
        if not self.recommendations:
            return Panel("点击扫描获取建议 / Click scan for recommendations", 
                        title="💡 优化建议 / Recommendations")
        
        content = []
        
        # 最佳信道建议 / Best channel recommendations
        content.append("[bold cyan]🎯 最佳信道推荐 / Best Channel Recommendations:[/bold cyan]")
        if self.recommendations.get('best_24ghz_channel'):
            content.append(f"  • 2.4GHz: 信道 {self.recommendations['best_24ghz_channel']} (干扰最少)")
        if self.recommendations.get('best_5ghz_channel'):
            content.append(f"  • 5GHz: 信道 {self.recommendations['best_5ghz_channel']} (干扰最少)")
        
        # 安全问题 / Security issues
        content.append("\n[bold yellow]🔒 安全提醒 / Security Alerts:[/bold yellow]")
        issues = self.recommendations.get('security_issues', [])
        if issues:
            for issue in issues:
                content.append(f"  ⚠️ {issue}")
        else:
            content.append("  ✅ 未发现明显安全问题 / No obvious security issues found")
        
        # 信号覆盖 / Signal coverage
        weak_count = self.recommendations.get('weak_signal_count', 0)
        content.append(f"\n[bold blue]📡 信号覆盖 / Signal Coverage:[/bold blue]")
        content.append(f"  • 检测到 {self.recommendations.get('total_networks', 0)} 个网络")
        content.append(f"  • {weak_count} 个网络信号较弱 (可能需要调整位置)")
        
        return Panel("\n".join(content), 
                    title="💡 优化建议 / Recommendations", 
                    border_style="yellow")


class WiFiDashApp(App):
    """
    WiFiDash TUI 主应用
    WiFiDash TUI Main Application
    """
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    #header {
        height: 3;
        content-align: center middle;
        text-style: bold;
    }
    
    #network-table {
        height: 50%;
        border: solid green;
    }
    
    #info-panel {
        height: 45%;
        margin-top: 1;
    }
    
    #channel-chart {
        width: 60%;
        height: 100%;
    }
    
    #recommendations {
        width: 40%;
        height: 100%;
    }
    
    #control-bar {
        height: auto;
        margin: 1 0;
    }
    
    .btn-scan {
        background: $success;
        color: $text;
    }
    
    .btn-export {
        background: $primary;
        color: $text;
    }
    
    .btn-auto {
        background: $warning;
        color: $text;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $surface-darken-1;
        color: $text;
        content-align: left middle;
        padding: 0 1;
    }
    
    DataTable {
        border: solid $primary;
    }
    
    TabbedContent {
        height: 100%;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出 / Quit"),
        Binding("r", "refresh", "刷新 / Refresh"),
        Binding("a", "auto_scan", "自动扫描 / Auto"),
        Binding("e", "export", "导出 / Export"),
        Binding("?", "help", "帮助 / Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.scanner = WiFiScanner()
        self.networks: List[WiFiNetwork] = []
        self.auto_scan_timer: Optional[Timer] = None
        self.is_auto_scanning = False
    
    def compose(self) -> ComposeResult:
        """构建UI / Build UI"""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            # 控制栏 / Control bar
            with Horizontal(id="control-bar"):
                yield Button("🔍 扫描网络 / Scan", id="btn-scan", variant="success")
                yield Button("🔄 自动扫描 / Auto", id="btn-auto", variant="warning")
                yield Button("📤 导出JSON / Export", id="btn-export", variant="primary")
                yield Label("", id="status-label")
            
            # 主内容区 / Main content area
            with TabbedContent():
                with TabPane("📶 网络列表 / Networks", id="tab-networks"):
                    yield NetworkTable(id="network-table")
                
                with TabPane("📊 信道分析 / Channels", id="tab-channels"):
                    yield ChannelChart(id="channel-chart")
                
                with TabPane("💡 建议 / Recommendations", id="tab-recommendations"):
                    yield RecommendationsPanel(id="recommendations")
                
                with TabPane("📋 日志 / Log", id="tab-log"):
                    yield RichLog(id="log", highlight=True)
        
        yield Footer()
    
    def on_mount(self):
        """应用挂载时 / On app mount"""
        self.title = "WiFiDash - 智能WiFi诊断工具"
        self.sub_title = "按 'r' 扫描网络 / Press 'r' to scan"
        
        log = self.query_one("#log", RichLog)
        log.write("[green]WiFiDash 已启动 / WiFiDash started[/green]")
        log.write("[blue]按 'r' 或点击扫描按钮开始扫描 / Press 'r' or click scan to start[/blue]")
        
        # 初始扫描 / Initial scan
        self.action_refresh()
    
    def on_button_pressed(self, event: Button.Pressed):
        """按钮点击处理 / Button press handler"""
        button_id = event.button.id
        
        if button_id == "btn-scan":
            self.action_refresh()
        elif button_id == "btn-auto":
            self.action_auto_scan()
        elif button_id == "btn-export":
            self.action_export()
    
    def action_refresh(self):
        """刷新/扫描动作 / Refresh/scan action"""
        self._update_status("正在扫描... / Scanning...")
        
        try:
            self.networks = self.scanner.scan()
            self._update_ui()
            self._update_status(f"扫描完成: 发现 {len(self.networks)} 个网络 / Scan complete: {len(self.networks)} networks found")
            
            log = self.query_one("#log", RichLog)
            log.write(f"[green]✓ 扫描完成 / Scan complete: {len(self.networks)} networks[/green]")
        except Exception as e:
            self._update_status(f"扫描失败 / Scan failed: {e}")
            log = self.query_one("#log", RichLog)
            log.write(f"[red]✗ 扫描错误 / Scan error: {e}[/red]")
    
    def action_auto_scan(self):
        """自动扫描开关 / Auto scan toggle"""
        if self.is_auto_scanning:
            self._stop_auto_scan()
        else:
            self._start_auto_scan()
    
    def _start_auto_scan(self):
        """开始自动扫描 / Start auto scan"""
        self.is_auto_scanning = True
        self.auto_scan_timer = self.set_interval(10, self.action_refresh)
        self._update_status("自动扫描已开启 (每10秒) / Auto scan enabled (every 10s)")
        
        btn = self.query_one("#btn-auto", Button)
        btn.label = "⏹ 停止自动 / Stop"
        btn.variant = "error"
        
        log = self.query_one("#log", RichLog)
        log.write("[yellow]▶ 自动扫描已开启 / Auto scan enabled[/yellow]")
    
    def _stop_auto_scan(self):
        """停止自动扫描 / Stop auto scan"""
        self.is_auto_scanning = False
        if self.auto_scan_timer:
            self.auto_scan_timer.stop()
            self.auto_scan_timer = None
        
        self._update_status("自动扫描已停止 / Auto scan stopped")
        
        btn = self.query_one("#btn-auto", Button)
        btn.label = "🔄 自动扫描 / Auto"
        btn.variant = "warning"
        
        log = self.query_one("#log", RichLog)
        log.write("[yellow]⏹ 自动扫描已停止 / Auto scan stopped[/yellow]")
    
    def action_export(self):
        """导出数据 / Export data"""
        if not self.networks:
            self._update_status("没有数据可导出 / No data to export")
            return
        
        try:
            filename = f"wifidash_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.scanner.export_to_json(self.networks, filename)
            self._update_status(f"已导出到 / Exported to: {filename}")
            
            log = self.query_one("#log", RichLog)
            log.write(f"[green]✓ 数据已导出 / Data exported: {filename}[/green]")
        except Exception as e:
            self._update_status(f"导出失败 / Export failed: {e}")
    
    def action_help(self):
        """显示帮助 / Show help"""
        log = self.query_one("#log", RichLog)
        log.write("""
[bold cyan]WiFiDash 帮助 / Help:[/bold cyan]
  [green]r[/green] - 扫描网络 / Scan networks
  [green]a[/green] - 切换自动扫描 / Toggle auto scan
  [green]e[/green] - 导出数据 / Export data
  [green]q[/green] - 退出 / Quit
  [green]?[/green] - 显示帮助 / Show help
        """)
    
    def _update_ui(self):
        """更新UI显示 / Update UI display"""
        # 更新网络表格 / Update network table
        table = self.query_one("#network-table", NetworkTable)
        table.update_networks(self.networks)
        
        # 更新信道图表 / Update channel chart
        channels = self.scanner.analyze_channels(self.networks)
        chart = self.query_one("#channel-chart", ChannelChart)
        chart.update_channels(channels)
        
        # 更新建议 / Update recommendations
        recs = self.scanner.get_recommendations(self.networks)
        rec_panel = self.query_one("#recommendations", RecommendationsPanel)
        rec_panel.update_recommendations(recs)
    
    def _update_status(self, message: str):
        """更新状态栏 / Update status bar"""
        label = self.query_one("#status-label", Label)
        label.update(message)


def main():
    """主入口函数 / Main entry function"""
    app = WiFiDashApp()
    app.run()


if __name__ == "__main__":
    main()
