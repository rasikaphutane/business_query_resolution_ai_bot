import pandas as pd

df = pd.read_csv("all_tickets_processed_improved_v3.csv")
df = (
    df.groupby("Topic_group", group_keys=False)
      .apply(lambda x: x.sample(n=min(1000, len(x))))
      .reset_index(drop=True)
)

df.to_csv("trimmed_tickets.csv", index=False)
