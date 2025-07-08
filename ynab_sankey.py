import pandas as pd
import plotly.graph_objects as go
from config.account_filter import account_filter

register_path = 'ynab_data/fake_register.csv'
# Common options are "Category Group" or "Category"
outflow_column = "Category Group"


df = pd.read_csv(register_path)

# Filter transactions to only include accounts where account_filter[account_name] is True
df = df[df['Account'].apply(lambda x: account_filter.get(x, False))]

# Exclude transfers where either source or destination account is in account_filter
# Transfers are identified by "Transfer : " in the Payee column
def is_transfer_involving_filtered_account(row):
    if 'Transfer : ' not in str(row['Payee']):
        return False

    # Extract the destination account from the transfer
    # Format is "Transfer : Account Name"
    transfer_dest = str(row['Payee']).replace('Transfer : ', '').strip()

    # Check if either the source account (row['Account']) or destination account is in account_filter
    source_in_filter = row['Account'] in account_filter
    dest_in_filter = transfer_dest in account_filter

    return source_in_filter or dest_in_filter

# Remove transfers involving any account in the filter
df = df[~df.apply(is_transfer_involving_filtered_account, axis=1)]

# Convert currency strings to numeric values
# Remove $ symbols and commas, then convert to numeric
df['Outflow'] = pd.to_numeric(df['Outflow'].str.replace('$', '').str.replace(',', ''), errors='coerce')
df['Inflow'] = pd.to_numeric(df['Inflow'].str.replace('$', '').str.replace(',', ''), errors='coerce')

# Convert Date column to datetime and filter from January 1, 2025 onwards
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
start_date = pd.to_datetime('2025-01-01') # Hardcoded start date
df = df[df['Date'] >= start_date]

# Example columns in your YNAB export: Date, Payee, Category, Memo, Outflow, Inflow, Account
# Actual Columns: "Account","Flag","Date","Payee","Category Group/Category","Category Group","Category","Memo","Outflow","Inflow","Cleared"
# Adjust based on your actual columns:
df['Amount'] = df['Inflow'] - df['Outflow']
df = df[df['Amount'] != 0]

# Create simplified Sankey: All inflows → Income bucket → Spending categories

# Step 1: Aggregate all inflows into a single "Income" bucket
df_inflows = df[df['Amount'] > 0].copy()
df_inflows['Source'] = df_inflows['Payee']  # Source is the payee (who paid you)
df_inflows['Target'] = 'Income'  # All inflows go to "Income" bucket

# Calculate transaction counts for inflows before grouping
inflow_counts = df_inflows.groupby('Source').size().to_dict()
df_inflows = df_inflows.groupby(['Source', 'Target']).Amount.sum().reset_index()

# Step 2: Aggregate all outflows from "Income" to spending category groups
df_outflows = df[df['Amount'] < 0].copy()
df_outflows['Source'] = 'Income'  # Source is the "Income" bucket
df_outflows['Target'] = df_outflows[outflow_column]

# Calculate transaction counts for outflows before grouping
outflow_counts = df_outflows.groupby(outflow_column).size().to_dict()
df_outflows = df_outflows.groupby(['Source', 'Target']).Amount.sum().abs().reset_index()

# Combine the flows
sankey_df = pd.concat([df_inflows, df_outflows])

# Create nodes
all_nodes = list(pd.unique(sankey_df[['Source', 'Target']].values.ravel()))

# Map nodes to indices
source_indices = sankey_df['Source'].apply(lambda x: all_nodes.index(x))
target_indices = sankey_df['Target'].apply(lambda x: all_nodes.index(x))

# Calculate statistics for annotations
# Load full dataset to calculate proper exclusions
full_df = pd.read_csv(register_path)
full_df['Date'] = pd.to_datetime(full_df['Date'], format='%m/%d/%Y')
full_df['Outflow'] = pd.to_numeric(full_df['Outflow'].str.replace('$', '').str.replace(',', ''), errors='coerce')
full_df['Inflow'] = pd.to_numeric(full_df['Inflow'].str.replace('$', '').str.replace(',', ''), errors='coerce')
full_df['Amount'] = full_df['Inflow'] - full_df['Outflow']

# Filter full dataset to time window only for exclusion calculation
time_window_df = full_df[full_df['Date'] >= start_date]
total_transactions_in_window = len(time_window_df)
filtered_transactions = len(df)
excluded_transactions = total_transactions_in_window - filtered_transactions

# Calculate max date for footer
max_date = df['Date'].max()

# Calculate other statistics
total_inflow = df[df['Amount'] > 0]['Amount'].sum()
total_outflow = abs(df[df['Amount'] < 0]['Amount'].sum())
net_flow = total_inflow - total_outflow
unique_accounts = len(df['Account'].unique())
unique_categories = len(df[outflow_column].unique())

# Create enhanced node labels with transaction counts
node_labels = []
for node in all_nodes:
    if node == 'Income':
        count = len(df_inflows)
        node_labels.append(f"{node}<br>({count} sources)")
    else:
        # Check if it's an inflow source (income source)
        if node in df_inflows['Source'].values:
            count = inflow_counts.get(node, 0)  # Use pre-calculated inflow counts
            amount = df_inflows[df_inflows['Source'] == node]['Amount'].sum()
            node_labels.append(f"{node}<br>({count} tx, ${amount:,.0f})")
        # Check if it's an outflow target (spending category)
        elif node in df_outflows['Target'].values:
            count = outflow_counts.get(node, 0)  # Use pre-calculated outflow counts
            amount = df_outflows[df_outflows['Target'] == node]['Amount'].sum()
            node_labels.append(f"{node}<br>({count} tx, ${amount:,.0f})")
        else:
            node_labels.append(node)

# Plot Sankey with enhanced labels
fig = go.Figure(go.Sankey(
    node={"label": node_labels},
    link={
        "source": source_indices,
        "target": target_indices,
        "value": sankey_df['Amount']
    }
))

# Update layout with comprehensive title and annotations
fig.update_layout(
    title_text=f"YNAB Cash Flow Sankey: {start_date.strftime('%B %Y')} Onwards",
    title_x=0.5,
    title_font_size=18,
    title_font_color="darkblue",
    font_size=10,
    height=800  # Increase height to accommodate annotations
)

print("=" * 50)
print("YNAB SNAKEY DATA SUMMARY")
print("=" * 50)
print(f"Filtered Transactions: {filtered_transactions:,}")
print(f"Unique Accounts: {unique_accounts}")
print(f"Unique Categories: {unique_categories}")
print(f"Total Inflow: ${total_inflow:,.2f}")
print(f"Total Outflow: ${total_outflow:,.2f}")
print("=" * 50)

# Add detailed inclusion annotation (top-left)
# annotation_text = f"""<b>INCLUDED DATA:</b><br>


# Format currency values separately
inflow_formatted = f"{total_inflow:,.2f} USD"
outflow_formatted = f"{total_outflow:,.2f} USD"
net_flow_formatted = f"({abs(net_flow):,.2f}) USD" if net_flow < 0 else f"{net_flow:,.2f} USD"

annotation_text = f"""<b>INCLUDED DATA:</b><br>
- {filtered_transactions:,} transactions across {unique_accounts} accounts and {unique_categories} spending categories<br>
- {inflow_formatted} total inflow<br>
- {outflow_formatted} total outflow<br>
- {net_flow_formatted} net"""
fig.add_annotation(
    text=annotation_text,
    x=0.02, y=1.10, xref="paper", yref="paper",
    showarrow=False, font=dict(size=10, color="darkblue"), align="left"
)

# Add data source footer with max date and excluded data
fig.add_annotation(
    text=f"Data: YNAB register.csv | Filtered by account_filter.py | Data through: {max_date.strftime('%Y-%m-%d')}",
    x=0.5, y=-0.05, xref="paper", yref="paper",
    showarrow=False, font=dict(size=10, color="gray"),
    align="center"
)

# Add excluded data annotation in footer
fig.add_annotation(
    text=f"🚫 EXCLUDED: {excluded_transactions:,} transactions (transfers, zero-amount, non-filtered accounts)",
    x=0.5, y=-0.08, xref="paper", yref="paper",
    showarrow=False, font=dict(size=10, color="red"),
    align="center"
)

# Add flow direction explanation
fig.add_annotation(
    text="<b>Flow Direction:</b> Income Sources → Income Bucket → Spending Categories",
    x=0.5, y=0.02, xref="paper", yref="paper",
    showarrow=False, font=dict(size=11, color="darkblue"),
    align="center", bgcolor="rgba(173, 216, 230, 0.7)"
)

fig.show()
