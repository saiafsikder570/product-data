import streamlit as st
import pandas as pd
import plotly.express as px
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

# ২. সাইডবার: মার্কেটিং ইনপুট
st.sidebar.header("🚀 মার্কেটিং সেটিংস")
usd_rate = st.sidebar.number_input("আজকের ডলার রেট (BDT)", value=130.0)
ad_spend_usd = st.sidebar.number_input("ফেসবুক অ্যাড স্পেন্ড (USD)", value=0.0)
ad_spend_bdt = ad_spend_usd * usd_rate

# ৩. ডাটা ক্লিন করার ফাংশন
def clean_val(val):
    if pd.isna(val) or val == "": return 0.0
    val = str(val).replace('৳', '').replace('%', '').replace(',', '').strip()
    try: return float(val)
    except: return 0.0

# ৪. ডাটা ইনপুট মেথড
COLUMN_LIST = [
    "প্রোডাক্টের নাম", "মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি চার্জ কোম্পানি বহন করবে", 
    "ডেলিভারি চার্জ কাস্টমার বহন করবে", "সেল প্রাইজ", "কয়টা অর্ডার", 
    "মোট প্রোডাক্ট দাম", "মোট রেভিনিউ / সেল", "রিটার্ন রেট", "এভারেজ লাভ"
]

st.subheader("📥 ডাটা আপডেট করুন")
if 'df_final' not in st.session_state:
    st.session_state.df_final = None

# কপি-পেস্ট টেবিল
input_df = st.data_editor(pd.DataFrame(columns=COLUMN_LIST), num_rows="dynamic", use_container_width=True, hide_index=True)

# ৫. ক্যালকুলেশন ইঞ্জিন
if st.button("📊 হিসাব ও রিপোর্ট জেনারেট করুন"):
    if not input_df.empty:
        df = input_df.copy()
        # ডাটা ক্লিন করা
        for col in ["মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি চার্জ কোম্পানি বহন করবে", 
                        "ডেলিভারি চার্জ কাস্টমার বহন করবে", "সেল প্রাইজ", "কয়টা অর্ডার", "রিটার্ন রেট"]:
            df[col] = df[col].apply(clean_val)
        
        # মূল হিসেব
        df["মোট প্রোডাক্ট দাম"] = df["মূল দাম"] * df["কয়টা অর্ডার"]
        df["মোট রেভিনিউ / সেল"] = (df["সেল প্রাইজ"] + df["ডেলিভারি চার্জ কাস্টমার বহন করবে"]) * df["কয়টা অর্ডার"]
        df["রিটার্ন রেট"] = df["রিটার্ন রেট"].apply(lambda x: x/100 if x > 1 else x)
        
        # নিট প্রফিট পার প্রোডাক্ট
        df["এভারেজ লাভ"] = ((df["মোট রেভিনিউ / সেল"] - (df["মোট প্রোডাক্ট দাম"]) - 
                            (df["প্যাকেজিং খরচ"] * df["কয়টা অর্ডার"]) - 
                            (df["ডেলিভারি চার্জ কোম্পানি বহন করবে"] * df["কয়টা অর্ডার"])) * (1 - df["রিটার্ন রেট"]))
        
        st.session_state.df_final = df
        st.session_state.summary = {
            "rev": df["মোট রেভিনিউ / সেল"].sum(),
            "base": df["মোট প্রোডাক্ট দাম"].sum(),
            "pack": (df["প্যাকেজিং খরচ"] * df["কয়টা অর্ডার"]).sum(),
            "delivery": (df["ডেলিভারি চার্জ কোম্পানি বহন করবে"] * df["কয়টা অর্ডার"]).sum(),
            "ret_loss": ((df["মোট রেভিনিউ / সেল"] - (df["মোট প্রোডাক্ট দাম"]) - (df["প্যাকেজিং খরচ"] * df["কয়টা অর্ডার"]) - (df["ডেলিভারি চার্জ কোম্পানি বহন করবে"] * df["কয়টা অর্ডার"])).sum()) * df["রিটার্ন রেট"].mean(),
            "net": df["এভারেজ লাভ"].sum() - ad_spend_bdt
        }

# ৬. ফলাফল প্রদর্শন
if st.session_state.df_final is not None:
    df = st.session_state.df_final
    s = st.session_state.summary
    roas = s['rev'] / ad_spend_bdt if ad_spend_bdt > 0 else 0

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("মোট রেভিনিউ", f"৳{s['rev']:,.0f}")
    c2.metric("অ্যাড খরচ (BDT)", f"৳{ad_spend_bdt:,.0f}")
    c3.metric("নিট লাভ", f"৳{s['net']:,.0f}")
    c4.metric("ROAS", f"{roas:.2f}x")

    # গ্রাফিক্যাল ভিউ
    st.subheader("📈 প্রোডাক্ট ভিত্তিক লাভ (Graph)")
    fig = px.bar(df[df["কয়টা অর্ডার"] > 0], x="প্রোডাক্টের নাম", y="এভারেজ লাভ", color="এভারেজ লাভ", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # বিস্তারিত রিপোর্ট টেবিল (এটি পুনরায় যুক্ত করা হয়েছে)
    st.subheader("📝 বিস্তারিত হিসাবকৃত রিপোর্ট")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # পিডিএফ জেনারেটর
    def create_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(200, 10, txt="Super Tasty Food", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(200, 8, txt="Location: Keshobpur, Jashore", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Daily Detailed Business Report", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 8, txt=f"Total Revenue: BDT {s['rev']:,.0f}", ln=True)
        pdf.cell(200, 8, txt=f"(-) Product Cost: BDT {s['base']:,.0f}", ln=True)
        pdf.cell(200, 8, txt=f"(-) Packaging Cost: BDT {s['pack']:,.0f}", ln=True)
        pdf.cell(200, 8, txt=f"(-) Delivery Cost: BDT {s['delivery']:,.0f}", ln=True)
        pdf.cell(200, 8, txt=f"(-) Ad Spend: BDT {ad_spend_bdt:,.0f}", ln=True)
        pdf.cell(200, 8, txt=f"(-) Return Loss Estimate: BDT {s['ret_loss']:,.0f}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"FINAL NET PROFIT: BDT {s['net']:,.0f}", ln=True)
        return pdf.output(dest='S').encode('latin-1', 'ignore')

    st.subheader("📥 ডাউনলোড সেকশন")
    pdf_file = create_pdf()
    st.download_button(label="📄 বিস্তারিত পিডিএফ রিপোর্ট ডাউনলোড", data=pdf_file, file_name="STF_Report.pdf", mime="application/pdf")

st.markdown("---")
st.caption("Developed by AI Assistant for Super Tasty Food")
