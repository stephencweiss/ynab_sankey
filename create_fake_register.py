import csv
import random
from datetime import datetime, timedelta
import calendar

def create_fake_register():
    # Define income accounts
    income_accounts = ["Job 1", "Job 2"]

    # Define categories
    categories = {
        "Home": ["Rent/Mortgage", "Utilities", "Home Maintenance", "Furniture"],
        "Clothes": ["Work Clothes", "Casual Clothes", "Shoes", "Accessories"],
        "Vacation": ["Airfare", "Hotels", "Food & Dining", "Activities", "Transportation"],
        "Car": ["Gas", "Insurance", "Maintenance", "Parking", "Car Payment"],
        "Gifts": ["Birthday Gifts", "Holiday Gifts", "Wedding Gifts", "Charitable Donations"]
    }

    # Define payees for each category
    payees = {
        "Home": ["Landlord", "ComEd", "Peoples Gas", "Home Depot", "IKEA"],
        "Clothes": ["Target", "Nordstrom", "Zara", "H&M", "Nike"],
        "Vacation": ["United Airlines", "Marriott", "Airbnb", "Uber", "Restaurant"],
        "Car": ["Shell", "State Farm", "Jiffy Lube", "City Parking", "Toyota Finance"],
        "Gifts": ["Amazon", "Target", "Local Store", "Charity Organization"]
    }

    # Generate transactions for the last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    transactions = []

    # Add income transactions
    for i in range(12):  # 12 income transactions (2 per month for 6 months)
        date = start_date + timedelta(days=i * 15)  # Every 15 days
        account = random.choice(income_accounts)
        amount = random.uniform(2000, 5000)  # Income between $2000-$5000

        transactions.append({
            "Account": account,
            "Flag": "",
            "Date": date.strftime("%m/%d/%Y"),
            "Payee": f"{account} Payroll",
            "Category Group/Category": "Inflow: Ready to Assign",
            "Category Group": "Inflow",
            "Category": "Ready to Assign",
            "Memo": f"Salary from {account}",
            "Outflow": "$0.00",
            "Inflow": f"${amount:.2f}",
            "Cleared": "Cleared"
        })

    # Add expense transactions
    for i in range(100):  # 100 expense transactions
        date = start_date + timedelta(days=random.randint(0, 180))
        category_group = random.choice(list(categories.keys()))
        category = random.choice(categories[category_group])
        payee = random.choice(payees[category_group])
        amount = random.uniform(10, 500)  # Expenses between $10-$500

        # Use different accounts for different types of expenses
        if category_group in ["Home", "Car"]:
            account = "Checking"
        else:
            account = random.choice(["Mastercard", "Visa", "Amex", "Discover"])

        transactions.append({
            "Account": account,
            "Flag": "",
            "Date": date.strftime("%m/%d/%Y"),
            "Payee": payee,
            "Category Group/Category": f"{category_group}: {category}",
            "Category Group": category_group,
            "Category": category,
            "Memo": f"Purchase at {payee}",
            "Outflow": f"${amount:.2f}",
            "Inflow": "$0.00",
            "Cleared": random.choice(["Cleared", "Uncleared"])
        })

    # Sort transactions by date
    transactions.sort(key=lambda x: datetime.strptime(x["Date"], "%m/%d/%Y"))

    # Write to CSV
    with open("ynab_data/fake_register.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Account", "Flag", "Date", "Payee", "Category Group/Category",
                     "Category Group", "Category", "Memo", "Outflow", "Inflow", "Cleared"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

    print(f"Created fake_register.csv with {len(transactions)} transactions")
    print(f"Date range: {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}")

if __name__ == "__main__":
    create_fake_register()