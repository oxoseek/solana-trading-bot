import streamlit as st
import requests
import pandas as pd
import joblib
from solana.rpc.api import Client
from collections import defaultdict

# 🔗 配置 Solana RPC & API
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6"
HELIUS_API_KEY = "你的HeliusAPIKey"
client = Client(SOLANA_RPC_URL)

# 🤖 加载 AI 交易预测模型
MODEL_PATH = "ai_model.pkl"  # 事先训练好的 AI 模型
ai_model = joblib.load(MODEL_PATH)

# 🎯 监控 KOL 钱包
KOL_WALLETS = [
    "Wallet_Address_1",
    "Wallet_Address_2",
    "Wallet_Address_3"
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

# 📈 AI 预测 KOL 交易行为
def predict_kol_trend(wallet_address):
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions?api-key={HELIUS_API_KEY}&limit=10"
    response = requests.get(url)
    transactions = response.json()
    
    data = []
    for tx in transactions:
        data.append([
            tx["blockTime"], 
            tx["fee"], 
            len(tx["tokenTransfers"]), 
            tx["solTransferAmount"]
        ])

    df = pd.DataFrame(data, columns=["Time", "Fee", "Transfers", "SOL_Amount"])
    prediction = ai_model.predict(df)
    return round(prediction.mean(), 2)  # 预测趋势分数

# 🌐 Streamlit Web UI
st.title("📈 Solana 智能交易 & 套利系统")

# 🔥 热门代币分析
st.subheader("🔥 共同持有代币")
common_tokens = get_common_holdings()
st.write(common_tokens)

# 🤖 AI 预测 KOL 交易趋势
st.subheader("📊 KOL 交易趋势预测")
trend_scores = {wallet: predict_kol_trend(wallet) for wallet in KOL_WALLETS}
st.write(trend_scores)

# 📡 交易执行面板
st.subheader("🚀 一键交易")
selected_token = st.selectbox("选择要交易的代币", common_tokens)
trade_amount = st.number_input("输入交易数量", min_value=1, step=1)

if st.button("⚡️ 执行交易"):
    st.write(f"正在执行交易：购买 {trade_amount} 个 {selected_token}...")
    # 这里可以调用交易函数执行实际交易（如 swap_token()）
    st.success("✅ 交易已成功执行！")

st.write("数据每 5 分钟自动刷新")
