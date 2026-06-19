import streamlit as st
import pandas as pd

# পেজ কনফিগারেশন
st.set_page_config(page_title="Professional Sales Dashboard", layout="wide")

# কাস্টম CSS স্টাইল
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { color: #2E4053; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 ডিজিটাল সেলস ও প্রফিট ট্র্যাকার")
st.write("নিচে আপনার পণ্যের তথ্য আপডেট করুন এবং অর্ডারের সংখ্যা বসিয়ে ফলাফল দেখুন।")

# প্রাথমিক ডেটা সেটআপ (আপনার স্ক্রিনশট অনুযায়ী)
initial_data = [
    ["মধু ছাড়া আখরোট (USA) ১ কেজি", 1100, 40, 85, 0, 1450, 0.15],
    ["মধু ছাড়া আখরোট (USA) ৭০০ গ্রাম", 770, 30, 85, 0, 1050, 0.15],
    ["মধু ছাড়া আখরোট (USA) ৫০০ গ্রাম", 550, 30, 85, 0, 800, 0.15],
    ["১ কেজি কাঠবাদাম + ১ কেজি কাজু + ১ কেজি আখরোট", 4140, 150, 145, 0, 5200, 0.15],
    ["২৫০ গ্রাম কাঠবাদাম + ২৫০ গ্রাম কাজু + ২৫০ গ্রাম আখরোট", 1035, 100, 0, 85, 1500, 0.15],
    ["৫০০ গ্রাম গোল্ডেন কিসমিস + ৫০০ গ্রাম ব্ল্যাক কিসমিস", 740, 60, 85, 0, 1100, 0.15],
    ["২৫০ গ্রাম কাজু + ২৫০ গ্রাম কাঠবাদাম", 685, 40, 0, 60, 950, 0.15]
]

columns = [
    "প্রোডাক্টের নাম", "মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি (কোম্পানি)", 
    "ডেলিভারি (কাস্টমার)", "সেল প্রাইজ", "রিটার্ন রেট"
]

df = pd.DataFrame(initial_data, columns=columns)
df["কয়টা অর্ডার"] = 0 # ইউজার ইনপুট কলাম

# ড্যাশবোর্ড ইনপুট সেকশন
st.subheader("📊 প্রোডাক্ট ডাটা এডিট করুন")
edited_df = st.data_editor(
    df,
    column_config={
        "কয়টা অর্ডার": st.column_config.NumberColumn("কয়টা অর্ডার", min_value=0, step=1),
        "রিটার্ন রেট": st.column_config.NumberColumn("রিটার্ন রেট (Decimal)", format="%.2f"),
    },
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True
)

# ক্যালকুলেশন লজিক
if not edited_df.empty:
    # মোট প্রোডাক্ট দাম = (মূল দাম + প্যাকেট খরচ + কোম্পানি ডেলিভারি খরচ) * অর্ডার
    edited_df["মোট প্রোডাক্ট দাম"] = (edited_df["মূল দাম"] + edited_df["প্যাকেজিং খরচ"] + edited_df["ডেলিভারি (কোম্পানি)"]) * edited_df["কয়টা অর্ডার"]
    
    # মোট রেভিনিউ = সেল প্রাইজ * অর্ডার
    edited_df["মোট রেভিনিউ"] = edited_df["সেল প্রাইজ"] * edited_df["কয়টা অর্ডার"]
    
    # এভারেজ লাভ = (মোট রেভিনিউ - মোট দাম) * (1 - রিটার্ন রেট)
    edited_df["এভারেজ লাভ"] = (edited_df["মোট রেভিনিউ"] - edited_df["মোট প্রোডাক্ট দাম"]) * (1 - edited_df["রিটার্ন রেট"])

    # সামারি ক্যালকুলেশন
    total_orders = edited_df["কয়টা অর্ডার"].sum()
    total_rev = edited_df["মোট রেভিনিউ"].sum()
    total_profit = edited_df["এভারেজ লাভ"].sum()
    total_cost = edited_df["মোট প্রোডাক্ট দাম"].sum()

    # রঙিন মেট্রিক ডিসপ্লে
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("মোট অর্ডার", f"{total_orders} টি", delta_color="normal")
    m2.metric("মোট রেভিনিউ", f"৳{total_rev:,.0f}", delta_color="normal")
    m3.metric("মোট খরচ", f"৳{total_cost:,.0f}", delta_color="inverse")
    m4.metric("নিট প্রফিট", f"৳{total_profit:,.0f}", delta_color="normal")

    # ফাইনাল টেবিল ডিসপ্লে
    st.subheader("📝 বিস্তারিত রিপোর্ট")
    st.dataframe(edited_df, use_container_width=True, hide_index=True)

    # ডাউনলোড বাটন
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 রিপোর্ট ডাউনলোড করুন (CSV)",
        data=csv,
        file_name='daily_sales_report.csv',
        mime='text/csv',
    )
else:
    st.warning("দয়া করে কিছু ডেটা ইনপুট দিন।")

st.markdown("---")
st.caption("Developed for Professional Digital Marketing Management")
