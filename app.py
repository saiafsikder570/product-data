import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io
import re

# ১. ব্র্যান্ডিং ও স্টাইল
st.set_page_config(page_title="Super Tasty Food - Pro Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 20px; border-radius: 15px; border-top: 5px solid #ff4b4b; }
    h1 { color: #ff4b4b; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍱 Super Tasty Food - প্রো সেলস ট্র্যাকার")
st.markdown("<p style='text-align: center;'>Keshobpur, Jashore</p>", unsafe_allow_html=True)

# ২. সাইডবার: মার্কেটিং ইনপুট
st.sidebar.header("🚀 মার্কেটিং এনালাইসিস")
usd_rate = st.sidebar.number_input("আজকের ডলার রেট (BDT)", value=125.0)
ad_spend_usd = st.sidebar.number_input("ফেসবুক অ্যাড স্পেন্ড (USD)", value=0.0)
ad_spend_bdt = ad_spend_usd * usd_rate

# ৩. ডাটা ক্লিন করার ফাংশন (৳, %, কমা পরিষ্কার করবে)
def clean_numeric(value):
    if pd.isna(value) or value == "": return 0.0
    if isinstance(value, str):
        # সংখ্যা ছাড়া বাকি সব (৳, %, কমা) বাদ দিবে
        value = re.sub(r'[^\d.]', '', value)
    try:
        return float(value)
    except:
        return 0.0

# ৪. ডাটা ইনপুট মেথড
COLUMN_LIST = [
    "প্রোডাক্টের নাম", "মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি চার্জ কোম্পানি বহন করবে", 
    "ডেলিভারি চার্জ কাস্টমার বহন করবে", "সেল প্রাইজ", "কয়টা অর্ডার", 
    "মোট প্রোডাক্ট দাম", "মোট রেভিনিউ / সেল", "রিটার্ন রেট", "এভারেজ লাভ"
]

st.subheader("📥 ডাটা আপডেট করুন")
input_tab1, input_tab2 = st.tabs(["📋 কপি-পেস্ট / ম্যানুয়াল", "📂 CSV আপলোড"])

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=COLUMN_LIST)

with input_tab1:
    st.write("শিট থেকে ১১টি কলাম কপি করে এখানে পেস্ট করুন।")
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True, hide_index=True)

with input_tab2:
    uploaded_file = st.file_uploader("CSV আপলোড করুন", type="csv")
    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file)
        edited_df = raw_df.reindex(columns=COLUMN_LIST).fillna(0)

# ৫. ক্যালকুলেশন ইঞ্জিন
if not edited_df.empty:
    # ডাটা ক্লিন করা
    for col in ["মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি চার্জ কোম্পানি বহন করবে", "সেল প্রাইজ", "কয়টা অর্ডার", "রিটার্ন রেট"]:
        edited_df[col] = edited_df[col].apply(clean_numeric)

    # ক্যালকুলেশন লজিক
    edited_df["মোট প্রোডাক্ট দাম"] = (edited_df["মূল দাম"] + edited_df["প্যাকেজিং খরচ"] + edited_df["ডেলিভারি চার্জ কোম্পানি বহন করবে"]) * edited_df["কয়টা অর্ডার"]
    edited_df["মোট রেভিনিউ / সেল"] = edited_df["সেল প্রাইজ"] * edited_df["কয়টা অর্ডার"]
    
    # রিটার্ন রেট যদি % এ থাকে (যেমন ১৫), তবে ১০০ দিয়ে ভাগ
    edited_df["রিটার্ন রেট"] = edited_df["রিটার্ন রেট"].apply(lambda x: x/100 if x > 1 else x)
    
    edited_df["এভারেজ লাভ"] = (edited_df["মোট রেভিনিউ / সেল"] - edited_df["মোট প্রোডাক্ট দাম"]) * (1 - edited_df["রিটার্ন রেট"])

    # সামারি মেট্রিক্স
    total_revenue = edited_df["মোট রেভিনিউ / সেল"].sum()
    total_cost = edited_df["মোট প্রোডাক্ট দাম"].sum()
    net_profit = total_revenue - total_cost - ad_spend_bdt
    roas = total_revenue / ad_spend_bdt if ad_spend_bdt > 0 else 0

    # মেট্রিক ডিসপ্লে
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("মোট রেভিনিউ", f"৳{total_revenue:,.0f}")
    c2.metric("অ্যাড খরচ (BDT)", f"৳{ad_spend_bdt:,.0f}")
    c3.metric("নিট লাভ", f"৳{net_profit:,.0f}")
    c4.metric("ROAS", f"{roas:.2f}x")

    st.subheader("📊 বিস্তারিত রিপোর্ট")
    st.dataframe(edited_df, use_container_width=True)

    # ৬. পিডিএফ জেনারেটর (সব ভেরিয়েবল ফিক্স করা)
    def create_pdf(rev, ad_bdt, profit, roas_val):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(200, 10, txt="Super Tasty Food", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 8, txt="Keshobpur, Jashore", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Daily Business Report Summary", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Total Revenue: BDT {rev:,.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Total Ad Spend: BDT {ad_bdt:,.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Net Profit: BDT {profit:,.2f}", ln=True)
        pdf.cell(200, 10, txt=f"ROAS: {roas_val:.2f}x", ln=True)
        return pdf.output(dest='S').encode('latin-1', 'ignore')

    # ডাউনলোড বাটন
    st.subheader("📥 ডাউনলোড করুন")
    try:
        pdf_file = create_pdf(total_revenue, ad_spend_bdt, net_profit, roas)
        st.download_button(label="📄 পিডিএফ রিপোর্ট ডাউনলোড", data=pdf_file, file_name="Daily_Report_STF.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"পিডিএফ তৈরিতে সমস্যা হচ্ছে: {e}")

st.markdown("---")
st.caption("Developed for Super Tasty Food Management")
