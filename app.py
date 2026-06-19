import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import re

# ১. ব্র্যান্ডিং ও ডিজাইন
st.set_page_config(page_title="Super Tasty Food Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 20px; border-radius: 15px; border-top: 5px solid #ff4b4b; }
    h1 { color: #ff4b4b; text-align: center; font-weight: bold; }
    .stButton>button { background: #ff4b4b; color: white; border-radius: 10px; width: 100%; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍱 Super Tasty Food - প্রফেশনাল ড্যাশবোর্ড")
st.markdown("<p style='text-align: center;'>Keshobpur, Jashore</p>", unsafe_allow_html=True)

# ২. মার্কেটিং ইনপুট (সাইডবার)
st.sidebar.header("🚀 মার্কেটিং সেটিংস")
usd_rate = st.sidebar.number_input("আজকের ডলার রেট (BDT)", value=125.0)
ad_spend_usd = st.sidebar.number_input("ফেসবুক অ্যাড স্পেন্ড (USD)", value=0.0)
ad_spend_bdt = ad_spend_usd * usd_rate

# ৩. ডাটা ক্লিন করার ফাংশন
def clean_val(val):
    if pd.isna(val) or val == "": return 0.0
    val = str(val).replace('৳', '').replace('%', '').replace(',', '').strip()
    try: return float(val)
    except: return 0.0

# ৪. ডাটা ইনপুট
COLUMN_LIST = [
    "প্রোডাক্টের নাম", "মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি চার্জ কোম্পানি বহন করবে", 
    "ডেলিভারি চার্জ কাস্টমার বহন করবে", "সেল প্রাইজ", "কয়টা অর্ডার", 
    "মোট প্রোডাক্ট দাম", "মোট রেভিনিউ / সেল", "রিটার্ন রেট", "এভারেজ লাভ"
]

st.subheader("📥 ডাটা আপডেট করুন (গুগল শিট থেকে কপি-পেস্ট করুন)")
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = pd.DataFrame(columns=COLUMN_LIST)

# ইউজার ইনপুট টেবিল
input_df = st.data_editor(st.session_state.raw_df, num_rows="dynamic", use_container_width=True, hide_index=True)

# ৫. ক্যালকুলেশন ইঞ্জিন (বাটন ক্লিক করলে হিসেব হবে)
if st.button("📊 হিসাব করুন (Process & Calculate)"):
    if not input_df.empty:
        # ডাটা টাইপ ফিক্স করা
        for col in ["মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি চার্জ কোম্পানি বহন করবে", "সেল প্রাইজ", "কয়টা অর্ডার", "রিটার্ন রেট"]:
            input_df[col] = input_df[col].apply(clean_val)
        
        # মূল হিসেব
        input_df["মোট প্রোডাক্ট দাম"] = (input_df["মূল দাম"] + input_df["প্যাকেজিং খরচ"] + input_df["ডেলিভারি চার্জ কোম্পানি বহন করবে"]) * input_df["কয়টা অর্ডার"]
        input_df["মোট রেভিনিউ / সেল"] = input_df["সেল প্রাইজ"] * input_df["কয়টা অর্ডার"]
        
        # রিটার্ন রেট এডজাস্টমেন্ট
        input_df["রিটার্ন রেট"] = input_df["রিটার্ন রেট"].apply(lambda x: x/100 if x > 1 else x)
        input_df["এভারেজ লাভ"] = (input_df["মোট রেভিনিউ / সেল"] - input_df["মোট প্রোডাক্ট দাম"]) * (1 - input_df["রিটার্ন রেট"])

        # রেজাল্ট দেখানো
        total_rev = input_df["মোট রেভিনিউ / সেল"].sum()
        total_cost = input_df["মোট প্রোডাক্ট দাম"].sum()
        net_profit = total_rev - total_cost - ad_spend_bdt
        roas = total_rev / ad_spend_bdt if ad_spend_bdt > 0 else 0

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("মোট রেভিনিউ", f"৳{total_rev:,.0f}")
        c2.metric("অ্যাড খরচ (BDT)", f"৳{ad_spend_bdt:,.0f}")
        c3.metric("নিট লাভ", f"৳{net_profit:,.0f}")
        c4.metric("ROAS", f"{roas:.2f}x")

        st.subheader("📝 বিস্তারিত রিপোর্ট (হিসাবকৃত)")
        st.dataframe(input_df, use_container_width=True)

        # ৬. পিডিএফ জেনারেটর
        def create_pdf(rev, ad, profit, roas_v):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 18)
            pdf.cell(200, 10, txt="Super Tasty Food", ln=True, align='C')
            pdf.set_font("Arial", '', 10)
            pdf.cell(200, 8, txt="Keshobpur, Jashore", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Business Report Summary", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Total Revenue: BDT {rev:,.0f}", ln=True)
            pdf.cell(200, 10, txt=f"Ad Spend: BDT {ad:,.0f}", ln=True)
            pdf.cell(200, 10, txt=f"Net Profit: BDT {profit:,.0f}", ln=True)
            pdf.cell(200, 10, txt=f"ROAS: {roas_v:.2f}x", ln=True)
            return pdf.output(dest='S').encode('latin-1', 'ignore')

        pdf_file = create_pdf(total_rev, ad_spend_bdt, net_profit, roas)
        st.download_button(label="📄 পিডিএফ রিপোর্ট ডাউনলোড", data=pdf_file, file_name="Daily_Report_STF.pdf", mime="application/pdf")
    else:
        st.warning("আগে ডাটা কপি-পেস্ট করুন।")

st.markdown("---")
st.caption("Developed by AI Assistant for Super Tasty Food")
