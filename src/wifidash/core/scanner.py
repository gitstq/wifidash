#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiDash 核心扫描模块
Core Scanner Module for WiFiDash

提供WiFi网络扫描、信号强度检测、信道分析等核心功能
Provides WiFi network scanning, signal strength detection, channel analysis
"""

import subprocess
import re
import json
import platform
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import threading
import time


@dataclass
class WiFiNetwork:
    """WiFi网络数据模型 / WiFi Network Data Model"""
    ssid: str
    bssid: str
    signal_dbm: int
    channel: int
    frequency: float
    security: str
    mode: str
    quality: int  # 0-100
    last_seen: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ChannelInfo:
    """信道信息数据模型 / Channel Information Data Model"""
    channel: int
    frequency: float
    usage_count: int
    avg_signal: float
    congestion_level: str  # Low, Medium, High
    networks: List[str]


class WiFiScanner:
    """
    WiFi扫描器核心类
    Core WiFi Scanner Class
    """
    
    # 2.4GHz信道频率映射 / 2.4GHz Channel Frequency Mapping
    CHANNEL_FREQ_24GHZ = {
        1: 2.412, 2: 2.417, 3: 2.422, 4: 2.427, 5: 2.432,
        6: 2.437, 7: 2.442, 8: 2.447, 9: 2.452, 10: 2.457,
        11: 2.462, 12: 2.467, 13: 2.472, 14: 2.484
    }
    
    # 5GHz信道频率映射 / 5GHz Channel Frequency Mapping
    CHANNEL_FREQ_5GHZ = {
        36: 5.180, 40: 5.200, 44: 5.220, 48: 5.240,
        52: 5.260, 56: 5.280, 60: 5.300, 64: 5.320,
        100: 5.500, 104: 5.520, 108: 5.540, 112: 5.560,
        116: 5.580, 120: 5.600, 124: 5.620, 128: 5.640,
        132: 5.660, 136: 5.680, 140: 5.700, 144: 5.720,
        149: 5.745, 153: 5.765, 157: 5.785, 161: 5.805,
        165: 5.825
    }
    
    def __init__(self):
        self.system = platform.system()
        self.scan_history: List[List[WiFiNetwork]] = []
        self.is_scanning = False
        self._stop_event = threading.Event()
    
    def _run_command(self, command: List[str]) -> Tuple[bool, str]:
        """
        执行系统命令 / Execute system command
        
        Args:
            command: 命令列表 / Command list
            
        Returns:
            (success, output): 执行状态和输出 / Execution status and output
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, str(e)
    
    def scan_linux(self) -> List[WiFiNetwork]:
        """
        Linux系统WiFi扫描 / WiFi scan for Linux systems
        
        Returns:
            List[WiFiNetwork]: 扫描到的网络列表 / List of scanned networks
        """
        networks = []
        
        # 使用iwlist扫描 / Use iwlist for scanning
        success, output = self._run_command(["iwlist", "scanning"])
        
        if not success:
            # 尝试使用nmcli / Try nmcli as fallback
            return self._scan_with_nmcli()
        
        # 解析iwlist输出 / Parse iwlist output
        cells = output.split("Cell ")
        
        for cell in cells[1:]:  # 跳过第一个空元素 / Skip first empty element
            try:
                network = self._parse_iwlist_cell(cell)
                if network:
                    networks.append(network)
            except Exception:
                continue
        
        return networks
    
    def _scan_with_nmcli(self) -> List[WiFiNetwork]:
        """
        使用nmcli扫描 / Scan using nmcli
        
        Returns:
            List[WiFiNetwork]: 扫描到的网络列表 / List of scanned networks
        """
        networks = []
        
        # 使用nmcli进行扫描 / Use nmcli for scanning
        success, output = self._run_command([
            "nmcli", "-t", "-f", 
            "SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY,MODE",
            "dev", "wifi", "list"
        ])
        
        if not success:
            return networks
        
        lines = output.strip().split('\n')
        seen_ssids = set()
        
        for line in lines:
            if not line or ':' not in line:
                continue
            
            parts = line.split(':')
            if len(parts) >= 7:
                ssid = parts[0] if parts[0] else "Hidden Network"
                bssid = parts[1] if parts[1] else "Unknown"
                
                # 去重 / Deduplication
                if ssid in seen_ssids and ssid != "Hidden Network":
                    continue
                seen_ssids.add(ssid)
                
                try:
                    channel = int(parts[2]) if parts[2] else 0
                    freq = float(parts[3].replace(' GHz', '')) if parts[3] else 0
                    signal = int(parts[4]) if parts[4] else -100
                    security = parts[5] if parts[5] else "Open"
                    mode = parts[6] if parts[6] else "Unknown"
                    
                    # 计算质量分数 / Calculate quality score
                    quality = self._calculate_quality(signal)
                    
                    network = WiFiNetwork(
                        ssid=ssid,
                        bssid=bssid,
                        signal_dbm=signal,
                        channel=channel,
                        frequency=freq,
                        security=security,
                        mode=mode,
                        quality=quality,
                        last_seen=datetime.now().isoformat()
                    )
                    networks.append(network)
                except (ValueError, IndexError):
                    continue
        
        return networks
    
    def _parse_iwlist_cell(self, cell: str) -> Optional[WiFiNetwork]:
        """
        解析iwlist单元格 / Parse iwlist cell
        
        Args:
            cell: iwlist单元格文本 / iwlist cell text
            
        Returns:
            Optional[WiFiNetwork]: 解析后的网络或None / Parsed network or None
        """
        # 提取ESSID / Extract ESSID
        ssid_match = re.search(r'ESSID:"([^"]*)"', cell)
        ssid = ssid_match.group(1) if ssid_match else "Hidden Network"
        
        # 提取BSSID / Extract BSSID
        bssid_match = re.search(r'Address:\s*([0-9A-Fa-f:]{17})', cell)
        bssid = bssid_match.group(1) if bssid_match else "Unknown"
        
        # 提取信号强度 / Extract signal strength
        signal_match = re.search(r'Signal level[=:](-?\d+)', cell)
        signal = int(signal_match.group(1)) if signal_match else -100
        
        # 提取信道 / Extract channel
        channel_match = re.search(r'Channel[:\s]*(\d+)', cell)
        channel = int(channel_match.group(1)) if channel_match else 0
        
        # 提取频率 / Extract frequency
        freq_match = re.search(r'Frequency[:\s]*([\d.]+)\s*GHz', cell)
        freq = float(freq_match.group(1)) if freq_match else 0
        
        # 提取加密方式 / Extract encryption
        if "WPA3" in cell or "SAE" in cell:
            security = "WPA3"
        elif "WPA2" in cell:
            security = "WPA2"
        elif "WPA" in cell:
            security = "WPA"
        elif "WEP" in cell:
            security = "WEP"
        elif "Encryption key:on" in cell:
            security = "Encrypted"
        else:
            security = "Open"
        
        # 提取模式 / Extract mode
        if "802.11ac" in cell or "VHT" in cell:
            mode = "802.11ac"
        elif "802.11n" in cell or "HT" in cell:
            mode = "802.11n"
        else:
            mode = "802.11g"
        
        quality = self._calculate_quality(signal)
        
        return WiFiNetwork(
            ssid=ssid,
            bssid=bssid,
            signal_dbm=signal,
            channel=channel,
            frequency=freq,
            security=security,
            mode=mode,
            quality=quality,
            last_seen=datetime.now().isoformat()
        )
    
    def _calculate_quality(self, signal_dbm: int) -> int:
        """
        计算信号质量分数 / Calculate signal quality score
        
        Args:
            signal_dbm: 信号强度(dBm) / Signal strength in dBm
            
        Returns:
            int: 质量分数(0-100) / Quality score (0-100)
        """
        # 信号质量映射 / Signal quality mapping
        if signal_dbm >= -50:
            return 100
        elif signal_dbm >= -60:
            return 80 + (signal_dbm + 60) * 2
        elif signal_dbm >= -70:
            return 60 + (signal_dbm + 70) * 2
        elif signal_dbm >= -80:
            return 40 + (signal_dbm + 80) * 2
        elif signal_dbm >= -90:
            return 20 + (signal_dbm + 90) * 2
        else:
            return max(0, signal_dbm + 100)
    
    def scan(self) -> List[WiFiNetwork]:
        """
        执行WiFi扫描 / Perform WiFi scan
        
        Returns:
            List[WiFiNetwork]: 扫描结果 / Scan results
        """
        if self.system == "Linux":
            networks = self.scan_linux()
        elif self.system == "Darwin":  # macOS
            networks = self.scan_macos()
        else:
            # Windows或其他系统使用模拟数据 / Windows or other use simulated data
            networks = self._generate_demo_networks()
        
        # 保存到历史记录 / Save to history
        self.scan_history.append(networks)
        if len(self.scan_history) > 100:
            self.scan_history.pop(0)
        
        return networks
    
    def scan_macos(self) -> List[WiFiNetwork]:
        """
        macOS系统WiFi扫描 / WiFi scan for macOS systems
        
        Returns:
            List[WiFiNetwork]: 扫描到的网络列表 / List of scanned networks
        """
        networks = []
        
        success, output = self._run_command([
            "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
            "-s"
        ])
        
        if not success:
            return self._generate_demo_networks()
        
        lines = output.strip().split('\n')[1:]  # 跳过标题行 / Skip header
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 7:
                try:
                    ssid = parts[0]
                    bssid = parts[1]
                    signal = int(parts[2])
                    channel = int(parts[3])
                    
                    # 确定频率 / Determine frequency
                    if channel <= 14:
                        freq = self.CHANNEL_FREQ_24GHZ.get(channel, 2.4)
                    else:
                        freq = self.CHANNEL_FREQ_5GHZ.get(channel, 5.0)
                    
                    security = ' '.join(parts[6:]) if len(parts) > 6 else "Open"
                    mode = "802.11n/ac"
                    quality = self._calculate_quality(signal)
                    
                    network = WiFiNetwork(
                        ssid=ssid,
                        bssid=bssid,
                        signal_dbm=signal,
                        channel=channel,
                        frequency=freq,
                        security=security,
                        mode=mode,
                        quality=quality,
                        last_seen=datetime.now().isoformat()
                    )
                    networks.append(network)
                except (ValueError, IndexError):
                    continue
        
        return networks
    
    def _generate_demo_networks(self) -> List[WiFiNetwork]:
        """
        生成演示网络数据 / Generate demo network data
        
        Returns:
            List[WiFiNetwork]: 演示网络列表 / Demo network list
        """
        demo_networks = [
            WiFiNetwork(
                ssid="Home_WiFi_5G",
                bssid="AA:BB:CC:DD:EE:01",
                signal_dbm=-45,
                channel=36,
                frequency=5.180,
                security="WPA3",
                mode="802.11ac",
                quality=95,
                last_seen=datetime.now().isoformat()
            ),
            WiFiNetwork(
                ssid="Home_WiFi_2.4G",
                bssid="AA:BB:CC:DD:EE:02",
                signal_dbm=-55,
                channel=6,
                frequency=2.437,
                security="WPA2",
                mode="802.11n",
                quality=85,
                last_seen=datetime.now().isoformat()
            ),
            WiFiNetwork(
                ssid="Neighbor_AP_1",
                bssid="11:22:33:44:55:01",
                signal_dbm=-65,
                channel=1,
                frequency=2.412,
                security="WPA2",
                mode="802.11n",
                quality=70,
                last_seen=datetime.now().isoformat()
            ),
            WiFiNetwork(
                ssid="Neighbor_AP_2",
                bssid="11:22:33:44:55:02",
                signal_dbm=-72,
                channel=6,
                frequency=2.437,
                security="WPA",
                mode="802.11g",
                quality=55,
                last_seen=datetime.now().isoformat()
            ),
            WiFiNetwork(
                ssid="CoffeeShop_Free",
                bssid="AA:BB:CC:11:22:33",
                signal_dbm=-78,
                channel=11,
                frequency=2.462,
                security="Open",
                mode="802.11n",
                quality=40,
                last_seen=datetime.now().isoformat()
            ),
            WiFiNetwork(
                ssid="Office_Network",
                bssid="44:55:66:77:88:99",
                signal_dbm=-52,
                channel=149,
                frequency=5.745,
                security="WPA2-Enterprise",
                mode="802.11ac",
                quality=88,
                last_seen=datetime.now().isoformat()
            ),
        ]
        return demo_networks
    
    def analyze_channels(self, networks: List[WiFiNetwork]) -> List[ChannelInfo]:
        """
        分析信道使用情况 / Analyze channel usage
        
        Args:
            networks: WiFi网络列表 / WiFi network list
            
        Returns:
            List[ChannelInfo]: 信道分析结果 / Channel analysis results
        """
        channel_data: Dict[int, Dict] = {}
        
        for network in networks:
            ch = network.channel
            if ch not in channel_data:
                freq = network.frequency
                channel_data[ch] = {
                    'frequency': freq,
                    'signals': [],
                    'networks': []
                }
            channel_data[ch]['signals'].append(network.signal_dbm)
            channel_data[ch]['networks'].append(network.ssid)
        
        results = []
        for ch, data in sorted(channel_data.items()):
            avg_signal = sum(data['signals']) / len(data['signals'])
            usage = len(data['networks'])
            
            # 确定拥堵等级 / Determine congestion level
            if usage <= 1:
                congestion = "Low"
            elif usage <= 3:
                congestion = "Medium"
            else:
                congestion = "High"
            
            results.append(ChannelInfo(
                channel=ch,
                frequency=data['frequency'],
                usage_count=usage,
                avg_signal=avg_signal,
                congestion_level=congestion,
                networks=data['networks']
            ))
        
        return results
    
    def get_recommendations(self, networks: List[WiFiNetwork]) -> Dict:
        """
        获取网络优化建议 / Get network optimization recommendations
        
        Args:
            networks: WiFi网络列表 / WiFi network list
            
        Returns:
            Dict: 优化建议 / Optimization recommendations
        """
        channels = self.analyze_channels(networks)
        
        # 找出最佳信道 / Find best channels
        best_24ghz = None
        best_5ghz = None
        
        for ch in channels:
            if ch.frequency < 3.0:  # 2.4GHz
                if best_24ghz is None or ch.usage_count < best_24ghz.usage_count:
                    best_24ghz = ch
            else:  # 5GHz
                if best_5ghz is None or ch.usage_count < best_5ghz.usage_count:
                    best_5ghz = ch
        
        # 检查安全问题 / Check security issues
        security_issues = []
        for net in networks:
            if net.security == "Open":
                security_issues.append(f"{net.ssid}: 开放网络 / Open network")
            elif net.security == "WEP":
                security_issues.append(f"{net.ssid}: 使用已破解的WEP加密 / Using cracked WEP encryption")
        
        # 信号覆盖分析 / Signal coverage analysis
        weak_signals = [net for net in networks if net.signal_dbm < -70]
        
        return {
            "best_24ghz_channel": best_24ghz.channel if best_24ghz else None,
            "best_5ghz_channel": best_5ghz.channel if best_5ghz else None,
            "security_issues": security_issues,
            "weak_signal_count": len(weak_signals),
            "total_networks": len(networks),
            "channel_analysis": [{
                "channel": c.channel,
                "congestion": c.congestion_level,
                "networks": c.usage_count
            } for c in channels]
        }
    
    def continuous_scan(self, callback, interval: int = 5):
        """
        持续扫描模式 / Continuous scan mode
        
        Args:
            callback: 扫描结果回调函数 / Scan result callback function
            interval: 扫描间隔(秒) / Scan interval in seconds
        """
        self.is_scanning = True
        self._stop_event.clear()
        
        while not self._stop_event.is_set():
            networks = self.scan()
            callback(networks)
            self._stop_event.wait(interval)
    
    def stop_continuous_scan(self):
        """停止持续扫描 / Stop continuous scan"""
        self._stop_event.set()
        self.is_scanning = False
    
    def export_to_json(self, networks: List[WiFiNetwork], filepath: str):
        """
        导出扫描结果到JSON / Export scan results to JSON
        
        Args:
            networks: WiFi网络列表 / WiFi network list
            filepath: 输出文件路径 / Output file path
        """
        data = {
            "scan_time": datetime.now().isoformat(),
            "system": self.system,
            "network_count": len(networks),
            "networks": [net.to_dict() for net in networks]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
