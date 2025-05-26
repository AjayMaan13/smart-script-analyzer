import streamlit as st
from processor import analyze_receipt
from datetime import datetime

# Page setup
st.set_page_config(page_title="AI Receipt Analyzer", page_icon="🧾", layout="wide")

# Simple data functions
def save_receipt(results):
    if 'receipts' not in st.session_state: st.session_state.receipts = []
    st.session_state.receipts.append({"date": datetime.now().strftime("%Y-%m-%d"), **results})
    return len(st.session_state.receipts)

def get_stats():
    receipts = st.session_state.get('receipts', [])
    total = sum(r['total'] for r in receipts)
    return len(receipts), total, total/len(receipts) if receipts else 0

# Sidebar stats
count, total, avg = get_stats()
with st.sidebar:
    st.header("📊 Your Stats")
    st.metric("Receipts", count)
    st.metric("Total Spent", f"${total:.2f}")
    st.metric("Average", f"${avg:.2f}")
    
    st.divider()
    st.subheader("💡 Tips for Best Results")
    st.write("• Use clear, well-lit photos")
    st.write("• Keep receipt flat and straight")
    st.write("• Make sure text is readable")
    st.write("• Portrait orientation preferred")

# Main app
st.title("🧾 AI Receipt Analyzer")
st.write("**Transform receipt photos into intelligent insights with AI**")

# Instructions
st.info("📋 **How it works:** Upload a receipt → AI extracts items & prices → Get spending insights → Save to track your expenses")

with st.expander("📱 See detailed instructions"):
    st.write("""
    **Step 1:** Take a clear photo of your receipt
    - Good lighting is essential
    - Avoid shadows and glare
    - Keep the receipt flat
    
    **Step 2:** Upload the image below
    - Supports JPG, PNG, JPEG formats
    - File size should be under 5MB
    
    **Step 3:** Review AI analysis
    - Check extracted items and prices
    - Read personalized insights
    
    **Step 4:** Save to track spending
    - Build your expense history
    - View analytics in sidebar
    """)

uploaded_file = st.file_uploader("Choose receipt image", type=['jpg', 'png', 'jpeg'], 
                                help="Upload a clear photo of your receipt for best results")

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 Your Receipt")
        st.image(uploaded_file, use_column_width=True)
        
        # Quality check
        with st.spinner("🤖 Analyzing..."):
            results = analyze_receipt(uploaded_file)
        
        quality = results.get('quality_score', 'Good')
        if quality in ['Fair', 'Poor']:
            st.warning(f"⚠️ Image quality: {quality}. Consider retaking for better results.")
        else:
            st.success(f"✅ Image quality: {quality}")
    
    with col2:
        st.subheader("📋 Results")
        
        # Items
        for i, item in enumerate(results['items'], 1):
            st.write(f"{i}. **{item['name']}** - ${item['price']:.2f}")
        
        st.metric("💰 Total", f"${results['total']:.2f}")
        
        # Insights
        st.subheader("💡 AI Insights")
        for insight in results['insights']:
            st.write(f"• {insight}")
    
    # Actions
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Receipt", use_container_width=True):
            count = save_receipt(results)
            st.success(f"Saved! Total receipts: {count}")
    with col2:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.receipts = []
            st.success("All data cleared!")
            st.rerun()

else:
    # Show example when no file uploaded
    st.markdown("### 🎯 Ready to get started?")
    st.write("Upload a receipt above to see AI analysis in action!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**✅ Works great with:**")
        st.write("• Grocery store receipts")
        st.write("• Restaurant bills")
        st.write("• Gas station receipts") 
        st.write("• Retail purchases")
    
    with col2:
        st.write("**❌ Avoid these:**")
        st.write("• Blurry or dark photos")
        st.write("• Handwritten receipts")
        st.write("• Heavily crumpled receipts")
        st.write("• Screenshots of receipts")