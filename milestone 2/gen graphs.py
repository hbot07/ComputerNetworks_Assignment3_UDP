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
plt.title("Sequence-number trace")
plt.grid()
plt.savefig("Sequence-number trace.jpeg")
plt.show()

zoom = len([i for i in graph_time_recv if i < 500])
plt.figure(figsize=(10, 5), dpi=150)
plt.scatter(graph_time_send[:zoom], graph_offset_send[:zoom], color='blue')
plt.scatter(graph_time_recv[:zoom], graph_offset_recv[:zoom], color='orange')
plt.xlabel("Time")
plt.ylabel("Offset")
plt.title("Zoomed in sequence-number trace")
plt.grid()
plt.savefig("Zoomed in sequence-number trace.jpeg")
plt.show()
