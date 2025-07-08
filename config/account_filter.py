# Account filter dictionary
# Set to False to include transactions from this account, False to exclude
account_filter = {
    "Job 1": True,
    "Job 2": True,
    "Checking": True,
    "Mastercard": True,
    "Visa": True,
    "Amex": True,
    "Discover": True,
}


# Example usage:
# To exclude an account, set it to False:
# account_filter["Cash"] = False
# account_filter["CC - Amazon"] = False

# To check if an account should be included:
# if account_filter.get(account_name, False):
#     # Include this transaction
#     pass