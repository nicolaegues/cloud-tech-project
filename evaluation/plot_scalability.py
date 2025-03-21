import pandas as pd
import matplotlib.pyplot as plt

filename = "hzz_cloud_tech\evaluation\hpa_metrics.csv"
names = ["CPU_usage", "Timestamp"]
y_label = "CPU usage over Time (%)"
fig_name = "hzz_cloud_tech\evaluation\cpu_vs_time.png"

df = pd.read_csv(filename, names=names)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

#time difference from the first timestamp (in seconds)
df["Time_Passed"] = (df["Timestamp"] - df["Timestamp"].iloc[0]).dt.total_seconds()
#df["Pods"] = df["Pods"].values - 4

# Plot
plt.figure(figsize=(10, 5))
plt.plot(df["Time_Passed"], df[names[0]], marker='o', linestyle='-')
plt.xlabel("Time (s)")
plt.ylabel(y_label)
plt.grid()
plt.savefig(fig_name, dpi = 300)
plt.show()
pass
