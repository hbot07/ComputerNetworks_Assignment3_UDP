NAME = "constant burst size 10"
import pickle

import matplotlib.pyplot as plt

with open("graph_send.pkl", 'rb') as f:
    graph_send = pickle.load(f)
with open("graph_rcv.pkl", 'rb') as f:
    graph_rcv = pickle.load(f)

graph_time_recv = [i[1] for i in graph_rcv]
graph_time_send = [i[1] for i in graph_send]
graph_offset_send = [i[0] for i in graph_send]
graph_offset_recv = [i[0] for i in graph_rcv]

plt.figure(figsize=(10, 5), dpi=150)
plt.scatter(graph_time_send, graph_offset_send, color='blue')
plt.scatter(graph_time_recv, graph_offset_recv, color='orange')
plt.xlabel("Time")
plt.ylabel("Offset")
plt.title(f"Sequence-number trace {NAME}")
plt.grid()
plt.savefig(f"graphs/{NAME}_1.jpeg")
plt.show()

zoom = len([i for i in graph_time_recv if i < 500])
plt.figure(figsize=(10, 5), dpi=150)
plt.scatter(graph_time_send[:zoom], graph_offset_send[:zoom], color='blue')
plt.scatter(graph_time_recv[:zoom], graph_offset_recv[:zoom], color='orange')
plt.xlabel("Time")
plt.ylabel("Offset")
plt.title(f"Zoomed in sequence-number trace {NAME}")
plt.grid()
plt.savefig(f"graphs/{NAME}_2.jpeg")
plt.show()

with open("graph_burst_send.pkl", 'rb') as f:
    graph_burst_send = pickle.load(f)
with open("graph_burst_rcv.pkl", 'rb') as f:
    graph_burst_rcv = pickle.load(f)

plt.figure(figsize=(10, 5), dpi=150)
plt.plot([i[1] for i in graph_burst_send], [i[0] for i in graph_burst_send], "-o", color='blue')
plt.xlabel("Time")
plt.ylabel("Burst Size")

# Create a twin of the original y-axis
ax2 = plt.gca().twinx()
# Plot the data on the twin y-axis
ax2.plot([i[1] for i in graph_burst_rcv], [i[0] for i in graph_burst_rcv], "-o",color='orange')
ax2.set_ylabel('Squished', color='orange')
ax2.tick_params('y', colors='orange')
ax2.set_ylim([-0.1, 1.75])

plt.grid()
plt.savefig(f"graphs/{NAME}_3.jpeg")
plt.show()