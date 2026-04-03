import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NodeFetcher:
    """节点获取器 - 从多个来源爬取免费节点"""
    
    def __init__(self):
        self.nodes = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data_dir = 'data'
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"创建数据目录: {self.data_dir}")
    
    def fetch_from_source1(self):
        """从来源1获取节点"""
        try:
            logger.info("正在从来源1获取节点...")
            # 示例：这里可以替换为实际的节点来源
            # 注意：这是一个示例实现
            url = "https://example.com/nodes"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析节点（根据实际网站结构调整）
            soup = BeautifulSoup(response.content, 'lxml')
            nodes = soup.find_all('div', class_='node')
            
            for node in nodes:
                try:
                    node_data = {
                        'url': node.get('data-url', ''),
                        'source': 'source1',
                        'added_at': datetime.now().isoformat(),
                        'valid': True
                    }
                    if node_data['url']:
                        self.nodes.append(node_data)
                except Exception as e:
                    logger.warning(f"解析节点失败: {e}")
            
            logger.info(f"从来源1获取了 {len(nodes)} 个节点")
        except Exception as e:
            logger.error(f"从来源1获取节点失败: {e}")
    
    def fetch_from_source2(self):
        """从来源2获取节点"""
        try:
            logger.info("正在从来源2获取节点...")
            # 示例：这里可以替换为实际的节点来源
            url = "https://example.com/nodes/api"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            nodes = data.get('nodes', [])
            
            for node in nodes:
                node_data = {
                    'url': node.get('url', ''),
                    'source': 'source2',
                    'added_at': datetime.now().isoformat(),
                    'valid': True
                }
                if node_data['url']:
                    self.nodes.append(node_data)
            
            logger.info(f"从来源2获取了 {len(nodes)} 个节点")
        except Exception as e:
            logger.error(f"从来源2获取节点失败: {e}")
    
    def remove_duplicates(self):
        """移除重复节点"""
        seen = set()
        unique_nodes = []
        
        for node in self.nodes:
            node_url = node.get('url', '')
            if node_url not in seen:
                seen.add(node_url)
                unique_nodes.append(node)
        
        removed_count = len(self.nodes) - len(unique_nodes)
        self.nodes = unique_nodes
        logger.info(f"移除了 {removed_count} 个重复节点")
    
    def save_nodes(self):
        """保存节点到JSON文件"""
        try:
            output_file = os.path.join(self.data_dir, 'nodes.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.nodes, f, ensure_ascii=False, indent=2)
            logger.info(f"节点已保存到 {output_file}")
            
            # 也保存为文本格式
            txt_file = os.path.join(self.data_dir, 'nodes.txt')
            with open(txt_file, 'w', encoding='utf-8') as f:
                for node in self.nodes:
                    f.write(f"{node['url']}\n")
            logger.info(f"节点已保存到 {txt_file}")
            
        except Exception as e:
            logger.error(f"保存节点失败: {e}")
    
    def run(self):
        """运行爬虫"""
        logger.info("=" * 50)
        logger.info("开始获取免费节点...")
        logger.info("=" * 50)
        
        # 从多个来源获取节点
        self.fetch_from_source1()
        self.fetch_from_source2()
        
        # 移除重复
        self.remove_duplicates()
        
        # 保存节点
        self.save_nodes()
        
        logger.info("=" * 50)
        logger.info(f"总共获取了 {len(self.nodes)} 个有效节点")
        logger.info("=" * 50)

if __name__ == '__main__':
    fetcher = NodeFetcher()
    fetcher.run()