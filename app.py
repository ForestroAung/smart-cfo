import streamlit as st
import os
import pandas as pd  # <-- NEW: The data manipulation tool
from extract import process_receipt

# --- PAGE SETUP ---
st.set_page_config(page_title="Smart Document CFO", page_icon="🧾")

st.title("📃 Smart Document CFO")
st.write("Upload a receipt, and I'll extract the data for you.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("About")
    st.write("Powered by Tesseract OCR and Meta Llama 3 (via Groq).")

# --- MAIN UPLOAD SECTION ---
uploaded_file = st.file_uploader("Choose a receipt image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="Your Receipt", use_container_width=True)

    with col2:
        st.write("### Extracted Data")
        if st.button("Analyze Receipt 🚀"):
            
            with st.spinner("Reading text and analyzing..."):
                temp_filename = "temp_receipt.jpg"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                data = process_receipt(temp_filename)
                
                if isinstance(data, str):
                    st.error(data)
                else:
                    st.success("Analysis Complete!")
                    
                    st.metric(label="Vendor", value=data.get('merchant_name', 'Unknown'))
                    st.metric(label="Total", value=f"{data.get('currency', '$')}{data.get('total_amount', '0.00')}")
                    
                    st.write(" **Details:**")
                    st.json(data)

                    # --- THE NEW PRO FEATURE ---
                    st.divider() # A nice visual line
                    st.write("### 💾 Export")
                    
                    # Convert the dictionary into a Pandas DataFrame (a spreadsheet format)
                    df = pd.DataFrame([data])
                    
                    # Convert the DataFrame into a CSV file format in memory
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    
                    # Create the download button
                    st.download_button(
                        label="Download as CSV 📥",
                        data=csv_data,
                        file_name="receipt_data.csv",
                        mime="text/csv"
                    )

                if os.path.exists(temp_filename):
                    os.remove(temp_filename)