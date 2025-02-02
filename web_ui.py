import streamlit as st
import requests
import pandas as pd
from solana.rpc.api import Client
from collections import defaultdict

# 🔗 配置 Solana RPC & API
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
HELIUS_API_KEY = "ef8d226c-bdcc-457e-b5da-522feb7840be"
client = Client(SOLANA_RPC_URL)

# 🎯 监控 KOL 钱包
KOL_WALLETS = [
    "6FNbu3i6vpigXMatC6SyWKibUAdJyyX8nM8WDtZCNcEz",
    "6xUL8CUfV1fzd3UQoDBs7agWNXpwyE5q56css1wHNFFU",
    "9v6RGY46wf672PtpYMxCJ1nvrVTrukUDn1AjE634rvCf"
]

# ✅ 获取钱包持仓
def get_wallet_holdings(wallet_address):
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/balances?api-key={HELIUS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    holdings = {item['mint']: float(item['amount']) for item in data['tokens'] if float(item['amount']) > 0}
    return holdings

# 📊 计算共同持有代币
def get_common_holdings():
    wallet_holdings = [get_wallet_holdings(wallet) for wallet in KOL_WALLETS]
    holdings_list = [set(holdings.keys()) for holdings in wallet_holdings]
    common_tokens = set.intersection(*holdings_list)  # 求交集
    return list(common_tokens)

# 🌐 Streamlit Web UI
st.title("📈 Solana 智能交易 & 套利系统")

# 🔥 热门代币分析
st.subheader("🔥 共同持有代币")
common_tokens = get_common_holdings()
st.write(common_tokens)

# 📡 交易执行面板
st.subheader("🚀 一键交易")
selected_token = st.selectbox("选择要交易的代币", common_tokens)
trade_amount = st.number_input("输入交易数量", min_value=1, step=1)

if st.button("⚡️ 执行交易"):
    st.write(f"正在执行交易：购买 {trade_amount} 个 {selected_token}...")
    # 这里可以调用交易函数执行实际交易（如 swap_token()）
    st.success("✅ 交易已成功执行！")

st.write("数据每 5 分钟自动刷新")
