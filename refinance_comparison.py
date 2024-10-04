import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime
import io

# Loan calculation functions
def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100
    n_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
    return payment

def remaining_balance(principal, annual_rate, years, months_paid):
    monthly_rate = annual_rate / 12 / 100
    n_payments = years * 12
    remaining = principal * ((1 + monthly_rate) ** n_payments - (1 + monthly_rate) ** months_paid) / ((1 + monthly_rate) ** n_payments - 1)
    return remaining

def cumulative_cost(monthly_payment, closing_costs, months):
    return monthly_payment * months + closing_costs

# Streamlit app setup
st.title("Refinance Comparison Tool")

# User inputs for original loan
original_principal = st.number_input("Original Loan Amount ($):", value=920000, step=10000)
original_rate = st.number_input("Original Interest Rate (%):", value=6.25, step=0.1)
loan_term_years = 30
first_payment_date = st.date_input("First Payment Date:", value=datetime(2023, 5, 1))

# User inputs for refinance options
st.subheader("Refinance Option 1")
refi_1_rate = st.number_input("Refi Option 1 Interest Rate (%):", value=5.5, step=0.1)
refi_1_points = st.number_input("Refi Option 1 Discount Points (%):", value=1.75, step=0.1) / 100
refi_1_closing_costs = st.number_input("Refi Option 1 Closing Costs ($):", value=5000, step=1000)
refi_1_date = st.date_input("Refi Option 1 Date:", value=datetime(2024, 11, 1))

st.subheader("Refinance Option 2")
refi_2_rate = st.number_input("Refi Option 2 Interest Rate (%):", value=5.25, step=0.1)
refi_2_points = st.number_input("Refi Option 2 Discount Points (%):", value=1.0, step=0.1) / 100
refi_2_closing_costs = st.number_input("Refi Option 2 Closing Costs ($):", value=5000, step=1000)
refi_2_date = st.date_input("Refi Option 2 Date:", value=datetime(2025, 12, 1))

# Calculations
months_paid_refi_1 = (refi_1_date.year - first_payment_date.year) * 12 + (refi_1_date.month - first_payment_date.month)
remaining_balance_refi_1 = remaining_balance(original_principal, original_rate, loan_term_years, months_paid_refi_1)

months_paid_refi_2 = (refi_2_date.year - first_payment_date.year) * 12 + (refi_2_date.month - first_payment_date.month)
remaining_balance_refi_2 = remaining_balance(original_principal, original_rate, loan_term_years, months_paid_refi_2)

new_principal_refi_1 = remaining_balance_refi_1 + (remaining_balance_refi_1 * refi_1_points) + refi_1_closing_costs
new_principal_refi_2 = remaining_balance_refi_2 + (remaining_balance_refi_2 * refi_2_points) + refi_2_closing_costs

original_monthly_payment = calculate_monthly_payment(original_principal, original_rate, loan_term_years)
refi_1_monthly_payment = calculate_monthly_payment(new_principal_refi_1, refi_1_rate, loan_term_years - (months_paid_refi_1 // 12))
refi_2_monthly_payment = calculate_monthly_payment(new_principal_refi_2, refi_2_rate, loan_term_years - (months_paid_refi_2 // 12))

# Cumulative cost comparison
months = np.arange(0, loan_term_years * 12, 1)
original_cumulative_cost = [cumulative_cost(original_monthly_payment, 0, m) for m in months]
refi_1_cumulative_cost = [cumulative_cost(refi_1_monthly_payment, refi_1_closing_costs, max(0, m - months_paid_refi_1)) + cumulative_cost(original_monthly_payment, 0, min(m, months_paid_refi_1)) for m in months]
refi_2_cumulative_cost = [cumulative_cost(refi_2_monthly_payment, refi_2_closing_costs, max(0, m - months_paid_refi_2)) + cumulative_cost(original_monthly_payment, 0, min(m, months_paid_refi_2)) for m in months]

# Interactive Plot with Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(x=months, y=original_cumulative_cost, mode='lines', name='Original Loan', line=dict(color='orange', dash='dash')))
fig.add_trace(go.Scatter(x=months, y=refi_1_cumulative_cost, mode='lines', name='Refi Option 1', line=dict(color='red')))
fig.add_trace(go.Scatter(x=months, y=refi_2_cumulative_cost, mode='lines', name='Refi Option 2', line=dict(color='green')))

fig.update_layout(
    title="Cumulative Cost Comparison of Refinance Scenarios",
    xaxis_title="Months Since Start",
    yaxis_title="Cumulative Cost (USD)",
    xaxis=dict(rangeslider=dict(visible=True)),
    yaxis=dict(automargin=True),
    legend=dict(x=0, y=1),
    template="plotly_white"
)

# Display the interactive plot
st.plotly_chart(fig, use_container_width=True)

# Add an option to download the plot
buffer = io.BytesIO()
fig.write_image(buffer, format='png')
st.download_button(
    label="Download Plot as PNG",
    data=buffer,
    file_name="cumulative_cost_comparison.png",
    mime="image/png"
)