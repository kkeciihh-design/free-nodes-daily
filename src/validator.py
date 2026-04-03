import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = 'data'
NODES_FILE = os.path.join(DATA_DIR, 'nodes.json')
TIMEOUT = 8
MAX_WORKERS = 12


def check_node(node_url):
    """Simple reachability check. For http/https URLs perform a GET; for other node formats this is a placeholder.
    Extend this function to support ss/vmess/vless/trojan etc. by performing protocol-level checks or using helper libraries."""
    try:
        if not node_url:
            return False
        if node_url.startswith('http://') or node_url.startswith('https://'):
            r = requests.get(node_url, timeout=TIMEOUT)
            return r.status_code == 200
        # Placeholder for non-HTTP schemes. Return False by default.
        return False
    except Exception as e:
        logger.debug(f'Node check exception for {node_url}: {e}')
        return False


def load_nodes():
    if not os.path.exists(NODES_FILE):
        return []
    with open(NODES_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            logger.error(f'Failed to load nodes file: {e}')
            return []


def save_nodes(nodes):
    out = os.path.join(DATA_DIR, 'nodes_validated.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    logger.info(f'Saved validation results to {out}')


def validate_all():
    nodes = load_nodes()
    if not nodes:
        logger.info('No nodes to validate')
        return

    logger.info(f'Starting validation for {len(nodes)} nodes')
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(check_node, n.get('url', '')): n for n in nodes}
        for fut in as_completed(futures):
            n = futures[fut]
            try:
                ok = fut.result()
            except Exception as e:
                logger.debug(f'Exception during validation: {e}')
                ok = False
            n['valid'] = bool(ok)
            n['checked_at'] = datetime.utcnow().isoformat() + 'Z'
            results.append(n)
            logger.debug(f"Validated: {n.get('url')} -> {n['valid']}")

    save_nodes(results)
    valid_count = sum(1 for r in results if r.get('valid'))
    logger.info(f'Validation finished: {valid_count}/{len(results)} available')


if __name__ == '__main__':
    validate_all()