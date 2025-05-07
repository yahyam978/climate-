import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import csv
from io import StringIO

# --- Data Setup ---
material_impacts = {
    "Ammonia": {"co2": 2.38, "water": 1.8, "energy": 38.0, "acidification": 0.022},
    "Ethylene": {"co2": 1.75, "water": 1.2, "energy": 78.0, "acidification": 0.015},
    "PVC": {"co2": 2.8, "water": 1.7, "energy": 62.0, "acidification": 0.028}
}

energy_impacts = {
    "Coal": {"co2": 1.02, "water": 0.004, "energy": 3.6, "acidification": 0.0012},
    "Natural Gas": {"co2": 0.49, "water": 0.002, "energy": 3.6, "acidification": 0.0003},
    "Solar": {"co2": 0.05, "water": 0.001, "energy": 3.6, "acidification": 0.0001}
}

# --- App Config ---
st.set_page_config(
    page_title="LCA Calculator",
    page_icon="🌱",
    layout="centered"
)

# --- PDF Generation (Unicode Fixed) ---
def create_pdf(material, mat_amount, energy_type, energy_amount, results_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title (using simple text to avoid Unicode)
    pdf.cell(200, 10, txt="LCA Calculation Report", ln=1, align='C')
    
    # Input parameters (ASCII only)
    pdf.cell(200, 10, txt=f"Material: {material} ({mat_amount} kg)", ln=1)
    pdf.cell(200, 10, txt=f"Energy: {energy_type} ({energy_amount} kWh)", ln=1)
    pdf.ln(10)
    
    # Results table (replace Unicode with plain text)
    pdf.set_font("Arial", size=10)
    col_widths = [70, 50, 30]
    
    # Header
    headers = ["Metric", "Value", "Score"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, txt=header, border=1)
    pdf.ln()
    
    # Rows
    for _, row in results_df.iterrows():
        metric = row['Metric'].replace("₂", "2").replace("₃", "3")  # Fix Unicode subscripts
        pdf.cell(col_widths[0], 10, txt=metric, border=1)
        pdf.cell(col_widths[1], 10, txt=row['Value'], border=1)
        pdf.cell(col_widths[2], 10, txt=str(row['Score']), border=1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin1', errors='replace')

# --- CSV Generation ---
def create_csv(results_df):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value", "Score"])
    for _, row in results_df.iterrows():
        writer.writerow([row['Metric'], row['Value'], row['Score']])
    return output.getvalue().encode('utf-8')

# --- Main App ---
def main():
    st.title("♻️ Chemical Process LCA Calculator")
    st.markdown("---")
    
    # Input Section
    col1, col2 = st.columns(2)
    with col1:
        material = st.selectbox("Select Material", list(material_impacts.keys()))
        material_amount = st.number_input("Amount (kg)", min_value=0.0, value=1.0, step=0.1)
    with col2:
        energy_type = st.selectbox("Energy Source", list(energy_impacts.keys()))
        energy_amount = st.number_input("Energy (kWh)", min_value=0.0, value=1.0, step=0.1)
    
    if st.button("Calculate Impact", type="primary"):
        # Calculations
        co2 = (material_impacts[material]["co2"] * material_amount) + (energy_impacts[energy_type]["co2"] * energy_amount)
        water = (material_impacts[material]["water"] * material_amount) + (energy_impacts[energy_type]["water"] * energy_amount)
        energy = (material_impacts[material]["energy"] * material_amount) + (energy_impacts[energy_type]["energy"] * energy_amount)
        acid = (material_impacts[material]["acidification"] * material_amount) + (energy_impacts[energy_type]["acidification"] * energy_amount)
        
        # Results DataFrame
        results_df = pd.DataFrame({
            "Metric": ["CO₂ Emissions", "Water Use", "Energy Demand", "Acidification"],
            "Value": [f"{co2:.2f} kg", f"{water:.2f} m³", f"{energy:.2f} MJ", f"{acid:.4f} kg SO₂-eq"],
            "Score": [min(int(co2/2)+1, 10), min(int(water/2)+1, 10), min(int(energy/50)+1, 10), min(int(acid*100)+1, 10)]
        })
        
        # Display Results
        st.success("### Results")
        st.dataframe(results_df, hide_index=True, use_container_width=True)
        
        # Export Buttons
        col1, col2 = st.columns(2)
        with col1:
            try:
                pdf_data = create_pdf(material, material_amount, energy_type, energy_amount, results_df)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name="lca_report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF Error: {str(e)}")
        
        with col2:
            csv_data = create_csv(results_df)
            st.download_button(
                label="📊 Download CSV Data",
                data=csv_data,
                file_name="lca_results.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
