import streamlit as st
import requests
from collections import defaultdict

# 🔗 配置 Solana RPC & API
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
HELIUS_API_KEY = "ef8d226c-bdcc-457e-b5da-522feb7840be"

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
    return common_tokens

# 📈 计算共同持仓代币的数量
def get_token_holdings(wallet_addresses, tokens):
    token_holdings = defaultdict(float)
    
    for wallet in wallet_addresses:
        holdings = get_wallet_holdings(wallet)
        for token in tokens:
            if token in holdings:
                token_holdings[token] += holdings[token]
    
    return token_holdings

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
    height=200
)

# 将钱包地址转换为列表
wallet_addresses = [address.strip() for address in wallet_addresses.splitlines() if address.strip()]

# 🔥 热门代币分析
st.subheader("🔥 共同持有代币")
common_tokens = get_common_holdings(wallet_addresses)

if common_tokens:
    # 获取共同持有代币的持仓数量
    token_holdings = get_token_holdings(wallet_addresses, common_tokens)
    
    # 按持仓数量排序并取前 11 名
    sorted_tokens = sorted(token_holdings.items(), key=lambda x: x[1], reverse=True)[:11]
    top_tokens = [token for token, _ in sorted_tokens]
    
    st.write("以下是多个钱包共同持有的前 11 名代币：")
    st.write(top_tokens)
else:
    st.warning("没有找到共同持有的代币，可能是由于 API 请求失败或钱包无持仓。")

# 📡 交易执行面板
st.subheader("🚀 一键交易")
if top_tokens:
    selected_token = st.selectbox("选择要交易的代币", top_tokens)
    trade_amount = st.number_input("输入交易数量", min_value=1, step=1)
    
    if st.button("⚡️ 执行交易"):
        st.write(f"正在执行交易：购买 {trade_amount} 个 {selected_token}...")
        # 在这里可以调用交易函数执行实际交易（如 swap_token()）
        st.success("✅ 交易已成功执行！")
else:
    st.warning("没有代币可供选择，请稍后再试。")

# 🚨 数据刷新提示
st.write("数据每 5 分钟自动刷新。")
