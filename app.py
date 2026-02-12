import streamlit as st
import ccxt

# --- 1. 安全金鑰讀取 (改用 Streamlit Secrets) ---
try:
    api_key = st.secrets["BINANCE_API_KEY"]
    secret_key = st.secrets["BINANCE_SECRET_KEY"]
except:
    st.warning("🔑 尚未設定 API 金鑰，請至 Streamlit 後台 Secrets 配置")
    st.stop()

# --- 2. 初始化連線 ---
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
})

st.set_page_config(page_title="獵人資產外掛", page_icon="🎯")
st.title("🎯 獵人實驗室：資產進度")

# --- 3. 核心功能：抓取 USDT 總額 ---
def get_total_usdt():
    total_usdt = 0
    try:
        # 掃描現貨
        balance = exchange.fetch_balance()
        total_usdt += balance['total'].get('USDT', 0)
        # 掃描合約
        future_bal = exchange.fetch_balance({'type': 'future'})
        total_usdt += future_bal['total'].get('USDT', 0)
        # 掃描理財
        try:
            earn = exchange.sapi_get_simple_earn_flexible_position()
            for pos in earn['rows']:
                if pos['asset'] == 'USDT':
                    total_usdt += float(pos['totalAmount'])
        except: pass
        return total_usdt
    except Exception as e:
        st.error(f"❌ 抓取失敗: {e}")
        return 0

# --- 4. 邏輯運算與顯示 ---
current_u = get_total_usdt()
base_target = 80.0  # 第一個里程碑

# 自動翻倍邏輯
target_u = base_target
while current_u >= target_u:
    target_u *= 2

last_target = target_u / 2 if target_u > base_target else 0
progress = min((current_u - last_target) / (target_u - last_target), 1.0)

# 網頁視覺化介面
st.divider()
st.metric("💰 目前 USDT 總資產", f"{current_u:.2f}")
st.write(f"下一階目標：**{target_u:.2f} USDT**")

# 進度條 (網頁版彩色條)
st.progress(progress)
st.write(f"📈 晉級進度：{progress*100:.1f}%")

if st.button('🔄 立即刷新餘額'):
    st.rerun()

st.divider()
if last_target > 0:
    st.success(f"✨ 已突破 {last_target:.2f}u 里程碑！繼續狩獵！")
