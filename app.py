import streamlit as st
import pandas as pd
import plotly.express as px
import io

# পেজ কনফিগারেশন
st.set_page_config(page_title="Super Tasty Food - Pro Dashboard", layout="wide", page_icon="🍱")

# কাস্টম স্টাইল (আধুনিক ফুড থিম)
st.markdown("""
    <style>
    .main { background-color: #111; color: #fff; }
    .stMetric { background: #222; padding: 20px; border-radius: 15px; border-left: 5px solid #ffcc00; }
    h1, h2 { color: #ffcc00; text-align: center; font-weight: bold; }
    .stButton>button { background: linear-gradient(45deg, #ff9900, #ffcc00); color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍱 Super Tasty Food - প্রফেশনাল ড্যাশবোর্ড")

# --- সাইডবার: মার্কেটিং সেটিংস ---
st.sidebar.header("🚀 মার্কেটিং এনালাইসিস")
usd_rate = st.sidebar.number_input("আজকের ডলার রেট (BDT)", value=125.0)
ad_spend_usd = st.sidebar.number_input("ফেসবুক অ্যাড স্পেন্ড (USD)", value=0.0)
ad_spend_bdt = ad_spend_usd * usd_rate

# --- ইনপুট মেথড সেকশন ---
st.subheader("📥 ডাটা ইনপুট মেথড")
input_tab1, input_tab2 = st.tabs(["📋 ম্যানুয়াল ও কপি-পেস্ট", "📂 CSV আপলোড"])

# ডিফল্ট ডাটা ফ্রেম
initial_df = pd.DataFrame([
    {"প্রোডাক্টের নাম": "মধু ছাড়া আখরোট ১ কেজি", "মূল দাম": 1100, "প্যাকেজিং": 40, "ডেলিভারি_কোম্পানি": 85, "সেল_প্রাইজ": 1750, "অর্ডার": 0},
    {"প্রোডাক্টের নাম": "১ কেজি স্পেশাল কম্বো (কাঠ+কাজু+আখরোট)", "মূল দাম": 4140, "প্যাকেজিং": 150, "ডেলিভারি_কোম্পানি": 145, "সেল_প্রাইজ": 5200, "অর্ডার": 0},
    {"প্রোডাক্টের নাম": "২৫০ গ্রাম মিক্সড ড্রাই ফ্রুট কম্বো", "মূল দাম": 1035, "প্যাকেজিং": 100, "ডেলিভারি_কোম্পানি": 0, "সেল_প্রাইজ": 1500, "অর্ডার": 0},
    {"প্রোডাক্টের নাম": "৫০০ গ্রাম গোল্ডেন ও ব্ল্যাক কিসমিস কম্বো", "মূল দাম": 740, "প্যাকেজিং": 60, "ডেলিভারি_কোম্পানি": 85, "সেল_প্রাইজ": 1100, "অর্ডার": 0},
])

with input_tab1:
    st.write("নিচের টেবিলে আপনি সরাসরি ডাটা টাইপ করতে পারেন অথবা গুগল শিট থেকে কপি করে পেস্ট করতে পারেন।")
    # 'num_rows="dynamic"' ব্যবহারের ফলে আপনি যত খুশি রো যোগ করতে পারবেন
    edited_df = st.data_editor(initial_df, num_rows="dynamic", use_container_width=True)

with input_tab2:
    uploaded_file = st.file_uploader("আপনার CSV ফাইলটি এখানে আপলোড করুন", type="csv")
    if uploaded_file:
        edited_df = pd.read_csv(uploaded_file)

# --- ক্যালকুলেশন ইঞ্জিন ---
if not edited_df.empty:
    # মোট প্রোডাক্ট কস্ট = (মূল দাম + প্যাকেজিং + ডেলিভারি) * অর্ডার
    edited_df["মোট খরচ"] = (edited_df["মূল দাম"] + edited_df["প্যাকেজিং"] + edited_df["ডেলিভারি_কোম্পানি"]) * edited_df["অর্ডার"]
    # মোট রেভিনিউ = সেল প্রাইজ * অর্ডার
    edited_df["মোট রেভিনিউ"] = edited_df["সেল_প্রাইজ"] * edited_df["অর্ডার"]
    
    total_revenue = edited_df["মোট রেভিনিউ"].sum()
    total_product_cost = edited_df["মোট খরচ"].sum()
    net_profit = total_revenue - total_product_cost - ad_spend_bdt
    roas = total_revenue / ad_spend_bdt if ad_spend_bdt > 0 else 0

    # --- মেট্রিক কার্ডস ---
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("মোট রেভিনিউ", f"৳{total_revenue:,.0f}")
    m2.metric("অ্যাড খরচ (BDT)", f"৳{ad_spend_bdt:,.0f}")
    m3.metric("নিট প্রফিট", f"৳{net_profit:,.0f}")
    m4.metric("ROAS", f"{roas:.2f}x")

    # --- গ্রাফিকাল ভিউ (অ্যানিমেশন সহ) ---
    st.subheader("📊 সেলস পারফরম্যান্স গ্রাফ")
    fig = px.bar(edited_df[edited_df["অর্ডার"] > 0], 
                 x="প্রোডাক্টের নাম", y="মোট রেভিনিউ", 
                 color="মোট রেভিনিউ", 
                 text_auto='.2s',
                 title="কোন প্রোডাক্ট থেকে কত আয় হলো",
                 template="plotly_dark",
                 color_continuous_scale='YlOrRd')
    st.plotly_chart(fig, use_container_width=True)

    # --- রিপোর্ট এক্সপোর্ট সেকশন ---
    st.subheader("📥 রিপোর্ট এক্সপোর্ট")
    
    # এক্সেল ফরম্যাটে ডাউনলোড (পিডিএফ এরর এড়াতে এটি সবচেয়ে ভালো ব্যবসার জন্য)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        edited_df.to_excel(writer, index=False, sheet_name='Daily_Report')
        # সামারি শিট
        summary_df = pd.DataFrame({"Category": ["Revenue", "Ad Spend", "Net Profit", "ROAS"],
                                  "Value": [total_revenue, ad_spend_bdt, net_profit, roas]})
        summary_df.to_excel(writer, index=False, sheet_name='Summary')
    
    st.download_button(
        label="📄 প্রফেশনাল এক্সেল রিপোর্ট ডাউনলোড করুন",
        data=buffer,
        file_name="Super_Tasty_Food_Report.xlsx",
        mime="application/vnd.ms-excel"
    )

st.markdown("---")
st.caption("© Super Tasty Food | Pro Business Management System")
