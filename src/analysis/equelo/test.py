from ...infra.connect import connect
history = connect()
dates = list(history.keys())
print(f"Loaded {len(history)} basho, {dates[0]} to {dates[-1]}")

