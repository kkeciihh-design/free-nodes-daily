import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NodeFetcher:
    """节点获取器 - 从多个来源爬取免费节点"""

    def __init__(self):
        self.nodes = []
        # 修复：原 User-Agent 字符串被截断，补全为合法值
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            )
        }
        self.data_dir = 'data'
        self.ensure_data_dir()

    def ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)  # 修复：exist_ok=True 更简洁，避免竞态条件
        logger.info(f"数据目录已就绪: {self.data_dir}")

    def fetch_from_source1(self):
        """从来源1获取节点（HTML 页面爬取示例，请替换为实际 URL 和解析逻辑）"""
        try:
            logger.info("正在从来源1获取节点...")
            url = "https://example.com/nodes"  # TODO: 替换为实际来源 URL
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            nodes = soup.find_all('div', class_='node')

            added = 0
            for node in nodes:
                try:
                    node_url = node.get('data-url', '').strip()
                    if node_url:
                        self.nodes.append({
                            'url': node_url,
                            'source': 'source1',
                            'added_at': datetime.now().isoformat(),
                            'valid': True
                        })
                        added += 1
                except Exception as e:
                    logger.warning(f"解析节点失败: {e}")

            logger.info(f"从来源1获取了 {added} 个节点")
        except Exception as e:
            logger.error(f"从来源1获取节点失败: {e}")

    def fetch_from_source2(self):
        """从来源2获取节点（JSON API 示例，请替换为实际 URL 和解析逻辑）"""
        try:
            logger.info("正在从来源2获取节点...")
            url = "https://example.com/nodes/api"  # TODO: 替换为实际来源 URL
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            nodes = data.get('nodes', [])

            added = 0
            for node in nodes:
                node_url = node.get('url', '').strip()
                if node_url:
                    self.nodes.append({
                        'url': node_url,
                        'source': 'source2',
                        'added_at': datetime.now().isoformat(),
                        'valid': True
                    })
                    added += 1

            logger.info(f"从来源2获取了 {added} 个节点")
        except Exception as e:
            logger.error(f"从来源2获取节点失败: {e}")

    def remove_duplicates(self):
        """移除重复节点（以 url 为唯一键）"""
        seen = set()
        unique_nodes = []
        for node in self.nodes:
            node_url = node.get('url', '')
            if node_url and node_url not in seen:
                seen.add(node_url)
                unique_nodes.append(node)

        removed_count = len(self.nodes) - len(unique_nodes)
        self.nodes = unique_nodes
        logger.info(f"移除了 {removed_count} 个重复节点，保留 {len(self.nodes)} 个")

    def save_nodes(self):
        """保存节点到 JSON 和 TXT 文件"""
        try:
            json_file = os.path.join(self.data_dir, 'nodes.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.nodes, f, ensure_ascii=False, indent=2)
            logger.info(f"节点已保存到 {json_file}")

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

        self.fetch_from_source1()
        self.fetch_from_source2()
        self.remove_duplicates()
        self.save_nodes()

        logger.info("=" * 50)
        logger.info(f"总共获取了 {len(self.nodes)} 个有效节点")
        logger.info("=" * 50)


if __name__ == '__main__':
    fetcher = NodeFetcher()
    fetcher.run()
