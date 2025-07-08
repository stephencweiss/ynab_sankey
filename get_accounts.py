#!/usr/bin/env python3
"""
Script to extract unique accounts from a YNAB register CSV file
and generate an account filter dictionary using pandas.
"""

import pandas as pd
import sys
from pathlib import Path


def extract_accounts_from_register(csv_path):
    """
    Extract unique account names from the register CSV file using pandas.

    Args:
        csv_path (str): Path to the register CSV file

    Returns:
        list: List of unique account names
    """
    try:
        # Read CSV with pandas - it handles BOM and encoding automatically
        df = pd.read_csv(csv_path)

        # Get unique accounts from the 'Account' column
        accounts = df['Account'].dropna().unique().tolist()

        # Sort the accounts alphabetically
        accounts.sort()

        return accounts

    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def generate_account_filter_dict(accounts):
    """
    Generate a dictionary with all accounts set to True by default.

    Args:
        accounts (list): List of account names

    Returns:
        dict: Account filter dictionary
    """
    return {account: True for account in accounts}


def save_account_filter(account_dict, output_path='account_filter.py'):
    """
    Save the account filter dictionary to a Python file.

    Args:
        account_dict (dict): Account filter dictionary
        output_path (str): Path to save the output file
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("# Account filter dictionary\n")
        file.write("# Set to True to include transactions from this account, False to exclude\n")
        file.write("account_filter = {\n")

        for account, include in account_dict.items():
            # Escape quotes in account names if needed
            escaped_account = account.replace('"', '\\"')
            file.write(f'    "{escaped_account}": {include},\n')

        file.write("}\n\n")
        file.write("# Example usage:\n")
        file.write("# To exclude an account, set it to False:\n")
        file.write("# account_filter[\"Cash\"] = False\n")
        file.write("# account_filter[\"CC - Amazon\"] = False\n\n")
        file.write("# To check if an account should be included:\n")
        file.write("# if account_filter.get(account_name, False):\n")
        file.write("#     # Include this transaction\n")
        file.write("#     pass\n")


def main():
    """Main function to run the script."""
    if len(sys.argv) != 2:
        print("Usage: python get_accounts.py <path_to_register.csv>")
        print("Example: python get_accounts.py ynab_data/register.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    print(f"Reading accounts from: {csv_path}")
    accounts = extract_accounts_from_register(csv_path)

    print(f"Found {len(accounts)} unique accounts:")
    for account in accounts:
        print(f"  - {account}")

    account_dict = generate_account_filter_dict(accounts)

    output_path = 'config/account_filter.py'
    save_account_filter(account_dict, output_path)

    print(f"\nAccount filter dictionary saved to: {output_path}")
    print("All accounts are set to True by default (included).")
    print("Edit the file to set specific accounts to False if you want to exclude them.")


if __name__ == "__main__":
    main()