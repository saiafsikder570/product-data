import streamlit as st
import pandas as pd

# পেজ সেটআপ
st.set_page_config(page_title="ডিজিটাল মার্কেটিং ড্যাশবোর্ড", layout="wide")

st.title("📊 সেলস ও প্রফিট ক্যালকুলেটর ড্যাশবোর্ড")
st.markdown("আপনার প্রতিদিনের অর্ডারের হিসাব এখানে আপডেট করুন।")

# নমুনা ডাটা (আপনার গুগল শিট অনুযায়ী)
# বাস্তবে আপনি আপনার গুগল শিটের CSV লিঙ্ক এখানে ব্যবহার করতে পারেন
data = {
    "প্রোডাক্টের নাম": [
        "মধু ছাড়া আখরোট (USA) ১ কেজি",
        "মধু ছাড়া আখরোট (USA) ৭০০ গ্রাম",
        "মধু ছাড়া আখরোট (USA) ৫০০ গ্রাম",
        "১ কেজি কাঠবাদাম + ১ কেজি কাজু + ১ কেজি আখরোট",
        "২৫০ গ্রাম কাঠবাদাম + ২৫০ গ্রাম কাজু + ২৫০ গ্রাম আখরোট",
        "৫০০ গ্রাম কাশ্মীরি গোল্ডেন কিসমিস + ৫০০ গ্রাম ব্ল্যাক কিসমিস"
    ],
    "মূল দাম": [1100, 770, 550, 4140, 1035, 740],
    "প্যাকেজিং খরচ": [40, 30, 30, 150, 100, 60],
    "ডেলিভারি (কোম্পানি)": [85, 85, 85, 145, 0, 85],
    "সেল প্রাইস": [1450, 1050, 800, 5200, 1500, 1100], # নমুনা সেল প্রাইস
    "রিটার্ন রেট (%)": [15, 15, 15, 15, 15, 15],
    "কয়টা অর্ডার": [0, 0, 0, 0, 0, 0] # এই ঘরটি আপনি এডিট করবেন
}

df = pd.DataFrame(data)

# এডিটেবল টেবিল তৈরি
st.subheader("📝 প্রতিদিনের অর্ডারের তথ্য ইনপুট দিন")
edited_df = st.data_editor(
    df,
    column_config={
        "কয়টা অর্ডার": st.column_config.NumberColumn(
            "কয়টা অর্ডার",
            help="আজকে কয়টি অর্ডার হয়েছে তা লিখুন",
            min_value=0,
            step=1,
            default=0,
        ),
    },
    disabled=["প্রোডাক্টের নাম", "মূল দাম", "প্যাকেজিং খরচ", "ডেলিভারি (কোম্পানি)", "সেল প্রাইস", "রিটার্ন রেট (%)"],
    hide_index=True,
)

# ক্যালকুলেশন লজিক
edited_df["মোট রেভিনিউ"] = edited_df["সেল প্রাইস"] * edited_df["কয়টা অর্ডার"]
edited_df["মোট খরচ"] = (edited_df["মূল দাম"] + edited_df["প্যাকেজিং খরচ"] + edited_df["ডেলিভারি (কোম্পানি)"]) * edited_df["কয়টা অর্ডার"]
edited_df["নিট লাভ"] = edited_df["মোট রেভিনিউ"] - edited_df["মোট খরচ"]

# সামারি সেকশন
total_orders = edited_df["কয়টা অর্ডার"].sum()
total_revenue = edited_df["মোট রেভিনিউ"].sum()
total_profit = edited_df["নিট লাভ"].sum()

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("মোট অর্ডার", f"{total_orders} টি")
with col2:
    st.metric("মোট রেভিনিউ", f"{total_revenue:,} টাকা")
with col3:
    st.metric("মোট সম্ভাব্য লাভ", f"{total_profit:,} টাকা", delta_color="normal")

# বিস্তারিত চার্ট (অপশনাল)
st.subheader("📈 প্রোডাক্ট ভিত্তিক লাভের গ্রাফ")
if total_orders > 0:
    st.bar_chart(data=edited_df, x="প্রোডাক্টের নাম", y="নিট লাভ")
else:
    st.info("অর্ডারের সংখ্যা বসালে এখানে অটোমেটিক গ্রাফ তৈরি হবে।")

st.write("---")
st.caption("Developed for Digital Marketers | Automated Business Dashboard")
