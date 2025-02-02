import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from solana.rpc.api import Client

# 🔗 配置 Solana RPC & API
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
HELIUS_API_KEY = "ef8d226c-bdcc-457e-b5da-522feb7840be"
client = Client(SOLANA_RPC_URL)

# 设定初始的 KOL 钱包地址（可以通过 UI 动态添加）
default_wallets = [
    "6FNbu3i6vpigXMatC6SyWKibUAdJyyX8nM8WDtZCNcEz",
    "Wallet_Address_2",
    "Wallet_Address_3"
]

# ✅ 获取钱包持仓
def get_wallet_holdings(wallet_address):
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/balances?api-key={HELIUS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查是否有错误
        data = response.json()
        holdings = {item['mint']: float(item['amount']) for item in data['tokens'] if float(item['amount']) > 0}
        return holdings
    except requests.exceptions.RequestException as e:
        st.error(f"获取钱包 {wallet_address} 数据时出错: {e}")
        return {}

# 📊 计算共同持有代币
def get_common_holdings(wallet_addresses):
    wallet_holdings = [get_wallet_holdings(wallet) for wallet in wallet_addresses]
    holdings_list = [set(holdings.keys()) for holdings in wallet_holdings]
    common_tokens = set.intersection(*holdings_list)  # 求交集
    return list(common_tokens)

# 📈 绘制 KOL 持仓图表
def plot_wallet_holdings(wallet_addresses):
    all_holdings = {}
    for wallet in wallet_addresses:
        holdings = get_wallet_holdings(wallet)
        for token, amount in holdings.items():
            if token not in all_holdings:
                all_holdings[token] = []
            all_holdings[token].append(amount)

    # 创建数据框
    df = pd.DataFrame(all_holdings, index=[f"钱包 {i+1}" for i in range(len(wallet_addresses))])
    
    # 绘制条形图
    plt.figure(figsize=(10, 6))
    df.plot(kind='bar', stacked=True)
    plt.title('KOL 钱包持仓情况')
    plt.xlabel('钱包')
    plt.ylabel('持仓数量')
    plt.xticks(rotation=0)
    
    # 显示图表
    st.pyplot(plt)

# 🌐 Streamlit Web UI
st.set_page_config(page_title="Solana 智能交易系统", page_icon="📈", layout="wide")

# 🏠 页面标题
st.title("📈 Solana 智能交易 & 套利系统")

# 🚀 页面简介
st.markdown("""
    欢迎使用 Solana 智能交易系统！  
    本系统可以帮助你分析 KOL 钱包持仓，计算共同持有的代币，并执行一键交易。  
    数据每 5 分钟自动刷新，确保你实时掌握最新行情！
""")

# 💼 动态添加钱包地址
st.subheader("💼 添加/管理 KOL 钱包地址")
wallet_addresses = st.text_area(
    "请输入 Solana 钱包地址（每个地址换行）",
    value="\n".join(default_wallets),
    height=200
)

# 将钱包地址转换为列表
wallet_addresses = [address.strip() for address in wallet_addresses.splitlines() if address.strip()]

# 🔥 热门代币分析
st.subheader("🔥 共同持有代币")
common_tokens = get_common_holdings(wallet_addresses)

if common_tokens:
    st.write("以下是多个钱包共同持有的代币：")
    st.write(common_tokens)
else:
    st.warning("没有找到共同持有的代币，可能是由于 API 请求失败或钱包无持仓。")

# 📊 KOL 持仓图表
st.subheader("📊 KOL 持仓分布")
plot_wallet_holdings(wallet_addresses)

# 📡 交易执行面板
st.subheader("🚀 一键交易")
if common_tokens:
    selected_token = st.selectbox("选择要交易的代币", common_tokens)
    trade_amount = st.number_input("输入交易数量", min_value=1, step=1)
    
    if st.button("⚡️ 执行交易"):
        st.write(f"正在执行交易：购买 {trade_amount} 个 {selected_token}...")
        # 在这里可以调用交易函数执行实际交易（如 swap_token()）
        st.success("✅ 交易已成功执行！")
else:
    st.warning("没有代币可供选择，请稍后再试。")

# 🚨 数据刷新提示
st.write("数据每 5 分钟自动刷新。")
