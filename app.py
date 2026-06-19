import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# পেজ কনফিগারেশন ও ব্র্যান্ডিং
st.set_page_config(page_title="Super Tasty Food Dashboard", layout="wide")

# কাস্টম ডিজাইন (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 20px; border-radius: 15px; border: 1px solid #ff4b4b; }
    h1, h2, h3 { color: #ff4b4b; font-family: 'SolaimanLipi', sans-serif; }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍎 Super Tasty Food - সেলস ও মার্কেটিং ড্যাশবোর্ড")

# সাইডবার সেটিংস
st.sidebar.header("⚙️ মার্কেটিং সেটিংস")
usd_rate = st.sidebar.number_input("আজকের ডলার রেট (BDT)", value=130.0, step=0.5)
ad_spend_usd = st.sidebar.number_input("মোট অ্যাড স্পেন্ড (USD)", value=0.0, step=1.0)
ad_spend_bdt = ad_spend_usd * usd_rate

st.sidebar.info(f"মোট অ্যাড খরচ: ৳ {ad_spend_bdt:,.2f}")

# প্রোডাক্ট ডেটা
products_data = {
    "প্রোডাক্টের নাম": [
        "মধু ছাড়া আখরোট ১ কেজি", "মধু ছাড়া আখরোট ৭০০ গ্রাম", "১ কেজি কম্বো প্যাক",
        "২৫০ গ্রাম কম্বো প্যাক", "কিসমিস ৫০০ গ্রাম প্যাক", "কাজু + কাঠবাদাম ২৫০ গ্রাম"
    ],
    "মূল দাম": [1100, 770, 4140, 1035, 740, 685],
    "প্যাকেজিং": [40, 30, 150, 100, 60, 40],
    "ডেলিভারি_কোম্পানি": [85, 85, 145, 0, 85, 0],
    "সেল_প্রাইজ": [1750, 1050, 5200, 1500, 1100, 950]
}

df = pd.DataFrame(products_data)
df["কয়টা অর্ডার"] = 0

# ইনপুট টেবিল
st.subheader("📝 প্রতিদিনের অর্ডারের তথ্য")
edited_df = st.data_editor(df, use_container_width=True, hide_index=True)

# ক্যালকুলেশন
edited_df["মোট খরচ"] = (edited_df["মূল দাম"] + edited_df["প্যাকেজিং"] + edited_df["ডেলিভারি_কোম্পানি"]) * edited_df["কয়টা অর্ডার"]
edited_df["মোট রেভিনিউ"] = edited_df["সেল_প্রাইজ"] * edited_df["কয়টা অর্ডার"]
total_rev = edited_df["মোট রেভিনিউ"].sum()
total_prod_cost = edited_df["মোট খরচ"].sum()
net_profit = total_rev - total_prod_cost - ad_spend_bdt

# ROAS ক্যালকুলেশন
roas = total_rev / ad_spend_bdt if ad_spend_bdt > 0 else 0

# মেট্রিক কার্ডস (Summary)
st.divider()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("মোট রেভিনিউ", f"৳{total_rev:,.0f}")
c2.metric("অ্যাড খরচ (BDT)", f"৳{ad_spend_bdt:,.0f}")
c3.metric("নিট লাভ", f"৳{net_profit:,.0f}")
c4.metric("ROAS", f"{roas:.2f}x")
c5.metric("মোট অর্ডার", f"{edited_df['কয়টা অর্ডার'].sum()} টি")

# গ্রাফিকাল রিপোর্ট (এনিমেশন সহ)
st.subheader("📈 সেলস এনালাইসিস")
fig = px.bar(edited_df, x="প্রোডাক্টের নাম", y="মোট রেভিনিউ", 
             color="মোট রেভিনিউ", template="plotly_dark", 
             title="প্রোডাক্ট ভিত্তিক আয়", barmode='group')
st.plotly_chart(fig, use_container_width=True)

# PDF জেনারেটর ফাংশন
def create_pdf(df, rev, profit, ad, roas_val):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Super Tasty Food - Daily Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Revenue: BDT {rev:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Ad Spend: BDT {ad:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Net Profit: BDT {profit:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"ROAS: {roas_val:.2f}x", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Order Details:", ln=True)
    for i, row in df.iterrows():
        if row['কয়টা অর্ডার'] > 0:
            pdf.cell(200, 8, txt=f"- {row['প্রোডাক্টের নাম']}: {row['কয়টা অর্ডার']} orders", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# PDF ডাউনলোড বাটন
st.subheader("📥 রিপোর্ট ডাউনলোড")
pdf_data = create_pdf(edited_df, total_rev, net_profit, ad_spend_bdt, roas)
st.download_button(label="📄 PDF রিপোর্ট ডাউনলোড করুন", 
                   data=pdf_data, 
                   file_name="daily_report.pdf", 
                   mime="application/pdf")

st.markdown("---")
st.caption("© Super Tasty Food | Dashboard v2.0")
