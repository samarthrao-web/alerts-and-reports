# Transaction_dimension.py

transaction_dim1 = [
  "payment_method_type",
  "txn_latency_enum"
]
  
transaction_dim2 = [ 
  "Order Type",
  "Auth Type",
  "Udf8"
]

# List of all dimension sets to iterate through
# Format: (dimension_list, descriptive_name)
ALL_DIMENSION_SETS = [
    (transaction_dim1, "transaction_dim1"),
    (transaction_dim2, "transaction_dim2"),
]