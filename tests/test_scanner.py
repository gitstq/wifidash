#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiDash 扫描器单元测试
WiFiDash Scanner Unit Tests
"""

import unittest
import sys
import os

# 添加src到路径 / Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wifidash.core.scanner import WiFiScanner, WiFiNetwork, ChannelInfo


class TestWiFiScanner(unittest.TestCase):
    """WiFiScanner测试类 / WiFiScanner Test Class"""
    
    def setUp(self):
        """测试前准备 / Setup before tests"""
        self.scanner = WiFiScanner()
    
    def test_calculate_quality_excellent(self):
        """测试优秀信号质量计算 / Test excellent signal quality calculation"""
        quality = self.scanner._calculate_quality(-45)
        self.assertEqual(quality, 100)
    
    def test_calculate_quality_good(self):
        """测试良好信号质量计算 / Test good signal quality calculation"""
        quality = self.scanner._calculate_quality(-60)
        self.assertEqual(quality, 80)
    
    def test_calculate_quality_fair(self):
        """测试一般信号质量计算 / Test fair signal quality calculation"""
        quality = self.scanner._calculate_quality(-75)
        self.assertEqual(quality, 50)
    
    def test_calculate_quality_poor(self):
        """测试差信号质量计算 / Test poor signal quality calculation"""
        quality = self.scanner._calculate_quality(-90)
        self.assertEqual(quality, 20)
    
    def test_generate_demo_networks(self):
        """测试演示数据生成 / Test demo data generation"""
        networks = self.scanner._generate_demo_networks()
        self.assertIsInstance(networks, list)
        self.assertGreater(len(networks), 0)
        
        # 检查网络属性 / Check network attributes
        for net in networks:
            self.assertIsInstance(net, WiFiNetwork)
            self.assertIsNotNone(net.ssid)
            self.assertIsNotNone(net.bssid)
            self.assertIsInstance(net.signal_dbm, int)
            self.assertIsInstance(net.channel, int)
    
    def test_analyze_channels(self):
        """测试信道分析 / Test channel analysis"""
        networks = self.scanner._generate_demo_networks()
        channels = self.scanner.analyze_channels(networks)
        
        self.assertIsInstance(channels, list)
        self.assertGreater(len(channels), 0)
        
        # 检查信道信息 / Check channel info
        for ch in channels:
            self.assertIsInstance(ch, ChannelInfo)
            self.assertIsInstance(ch.channel, int)
            self.assertIsInstance(ch.usage_count, int)
            self.assertIn(ch.congestion_level, ["Low", "Medium", "High"])
    
    def test_get_recommendations(self):
        """测试建议生成 / Test recommendation generation"""
        networks = self.scanner._generate_demo_networks()
        recs = self.scanner.get_recommendations(networks)
        
        self.assertIsInstance(recs, dict)
        self.assertIn("total_networks", recs)
        self.assertIn("security_issues", recs)
        self.assertIn("channel_analysis", recs)


class TestWiFiNetwork(unittest.TestCase):
    """WiFiNetwork数据类测试 / WiFiNetwork Data Class Tests"""
    
    def test_network_creation(self):
        """测试网络对象创建 / Test network object creation"""
        from datetime import datetime
        
        net = WiFiNetwork(
            ssid="TestNetwork",
            bssid="AA:BB:CC:DD:EE:FF",
            signal_dbm=-50,
            channel=6,
            frequency=2.437,
            security="WPA2",
            mode="802.11n",
            quality=90,
            last_seen=datetime.now().isoformat()
        )
        
        self.assertEqual(net.ssid, "TestNetwork")
        self.assertEqual(net.signal_dbm, -50)
        self.assertEqual(net.quality, 90)
    
    def test_to_dict(self):
        """测试转换为字典 / Test conversion to dict"""
        from datetime import datetime
        
        net = WiFiNetwork(
            ssid="TestNetwork",
            bssid="AA:BB:CC:DD:EE:FF",
            signal_dbm=-50,
            channel=6,
            frequency=2.437,
            security="WPA2",
            mode="802.11n",
            quality=90,
            last_seen=datetime.now().isoformat()
        )
        
        d = net.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["ssid"], "TestNetwork")
        self.assertEqual(d["signal_dbm"], -50)


if __name__ == '__main__':
    unittest.main()
