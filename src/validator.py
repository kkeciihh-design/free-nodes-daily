import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime, timezone  # 修复：导入 timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = 'data'
NODES_FILE = os.path.join(DATA_DIR, 'nodes.json')
TIMEOUT = 8
MAX_WORKERS = 12


def check_node(node_url: str) -> bool:
    """
    简单可达性检测。
    - http/https：发起 GET 请求，状态码 200 视为可用。
    - 其他协议（ss/vmess/vless/trojan 等）：当前为占位逻辑，返回 False。
      如需支持，可引入对应的协议检测库或实现 TCP 握手探测。
    """
    try:
        if not node_url:
            return False
        if node_url.startswith('http://') or node_url.startswith('https://'):
            r = requests.get(node_url, timeout=TIMEOUT)
            return r.status_code == 200
        # 修复：非 HTTP 协议给出明确日志，方便后续扩展
        logger.debug(f'跳过非 HTTP 节点（暂不支持协议检测）: {node_url}')
        return False
    except Exception as e:
        logger.debug(f'节点检测异常 {node_url}: {e}')
        return False


def load_nodes() -> list:
    if not os.path.exists(NODES_FILE):
        logger.warning(f'节点文件不存在: {NODES_FILE}')
        return []
    with open(NODES_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            logger.error(f'加载节点文件失败: {e}')
            return []


def save_nodes(nodes: list):
    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, 'nodes_validated.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    logger.info(f'验证结果已保存到 {out}')

    # 同时输出可用节点的纯文本列表，方便直接使用
    valid_txt = os.path.join(DATA_DIR, 'nodes_valid.txt')
    with open(valid_txt, 'w', encoding='utf-8') as f:
        for n in nodes:
            if n.get('valid'):
                f.write(f"{n['url']}\n")
    logger.info(f'可用节点列表已保存到 {valid_txt}')


def validate_all():
    nodes = load_nodes()
    if not nodes:
        logger.info('没有需要验证的节点')
        return

    logger.info(f'开始验证 {len(nodes)} 个节点...')
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(check_node, n.get('url', '')): n for n in nodes}
        for fut in as_completed(futures):
            n = futures[fut]
            try:
                ok = fut.result()
            except Exception as e:
                logger.debug(f'验证任务异常: {e}')
                ok = False
            n['valid'] = bool(ok)
            # 修复：datetime.utcnow() 在 Python 3.12 已弃用，改用 timezone-aware 写法
            n['checked_at'] = datetime.now(timezone.utc).isoformat()
            results.append(n)
            logger.debug(f"已验证: {n.get('url')} -> {n['valid']}")

    save_nodes(results)
    valid_count = sum(1 for r in results if r.get('valid'))
    logger.info(f'验证完成：{valid_count}/{len(results)} 个节点可用')


if __name__ == '__main__':
    validate_all()
