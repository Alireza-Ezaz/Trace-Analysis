# using babeltrace2 to parse lttng trace
import bt2
from sklearn.cluster import KMeans
import numpy as np

# Create a list of system calls.
system_calls = []

# Create a trace collection message iterator from our lttng trace using babeltrace2.
message_iterator = bt2.TraceCollectionMessageIterator("traces/kernel")

entry_timestamps = {}
system_call_durations = []
# finding all system calls with their duration
for index, message in enumerate(message_iterator):
    # `bt2._EventMessageConst` is the Python type of an event message.
    if type(message) is bt2._EventMessageConst:
        # print("event name {0} and cpu_id {1} at timestamp {2}".format(
        #     message.event.name,
        #     message.event["cpu_id"],
        #     message.default_clock_snapshot.ns_from_origin
        # ))
        if "syscall_entry" in message.event.name:
            syscall_name = message.event.name.replace("syscall_entry_", "")
            # setdefault(key, default) is a Python dictionary method.
            # If key exists in the dictionary, it returns the associated value.
            # If key doesn't exist, it inserts key with the value default into the dictionary and returns default.
            # In this case, key is syscall_name, and default is an empty list [].
            entry_timestamps.setdefault(syscall_name, []).append(message.default_clock_snapshot.ns_from_origin)
        elif "syscall_exit" in message.event.name:
            syscall_name = message.event.name.replace("syscall_exit_", "")
            entry_timestamp_list = entry_timestamps.get(syscall_name, [])
            if entry_timestamp_list:
                entry_timestamp = entry_timestamp_list.pop()
                duration = message.default_clock_snapshot.ns_from_origin - entry_timestamp
                system_call_durations.append((syscall_name, duration))

# print(system_call_durations)
# print()
print("*****************************************************")
print()
print("Number of system calls: " + str(len(system_call_durations)))
print("Duration is in nanoseconds")

# Clustering system calls by duration
# we are only interested in the duration of the system calls not the names
durations = [duration for name, duration in system_call_durations]

# Convert the list to a NumPy array for K-Means
# The -1 in the reshape function means that NumPy will automatically determine
# the size of one dimension while preserving the total number of elements.
# In this case, it's reshaping the array to have one column and as many rows as needed to accommodate all the data points.
# The reason for reshaping to one column is that K-Means expects the input data to be in the form of a 2D array,
# where each row represents a data point,
# and each column represents a feature.
# Since we have a single feature (the syscall duration), we reshape it into a single column.
X = np.array(durations).reshape(-1, 1)

# Apply K-Means clustering
# https://www.youtube.com/watch?v=4b5d3muPQmA
K = 3  # Define the number of clusters (you can adjust this)
kmeans = KMeans(n_clusters=K, random_state=0).fit(X)
labels = kmeans.labels_

# Analyze the results
for cluster in range(K):
    cluster_indices = np.where(labels == cluster)
    cluster_durations = X[cluster_indices]
    average_duration = np.mean(cluster_durations)
    print(f'Cluster {cluster + 1}:')
    print(f'Number of syscalls in cluster: {len(cluster_durations)}')
    print(f'Average duration: {average_duration:.2f} nanoseconds')
    print()

print("*****************************************************")
print(f"Number of system calls: {len(system_call_durations)}")
print("*****************************************************")
print()

# Find the names of system calls in Cluster 3
cluster_number = 2  # Assuming Cluster 3 is labeled as 2
indices_in_cluster_3 = np.where(labels == cluster_number)

print("System calls in Cluster 3:")
for index in indices_in_cluster_3[0]:
    syscall_name, _ = system_call_durations[index]
    print(syscall_name)

print("*****************************************************")
print(f"Number of system calls: {len(system_call_durations)}")
# The results of your K-Means clustering indicate that the system call durations have been grouped into three clusters.
# Let's interpret the results:
#
# Cluster 1:
#
# Number of system calls in cluster: 26,785
# Average duration: 2,067,626.77 nanoseconds
# This cluster contains a large number of system calls (26,785) with relatively short durations.
# The average duration for this cluster is 2,067,626.77 nanoseconds, which is approximately 2 milliseconds.
# These are likely system calls that execute quickly and are part of the normal operation of your system.
#
# Cluster 2:
#
# Number of system calls in cluster: 3
# Average duration: 12,653,168,777.33 nanoseconds
# Cluster 2 contains a very small number of system calls (3) with extremely long durations.
# The average duration for this cluster is 12,653,168,777.33 nanoseconds, which is approximately 12.65 seconds.
# These syscalls have significantly longer execution times compared to those in Cluster 1
# and might represent rare or unusually time-consuming operations.
#
# Cluster 3:
#
# Number of system calls in cluster: 44
# Average duration: 1,090,388,664.73 nanoseconds
# Cluster 3 contains 44 system calls with durations that are relatively moderate in length.
# The average duration for this cluster is 1,090,388,664.73 nanoseconds, which is approximately 1.09 seconds.
# These syscalls have durations that fall between the very short durations of Cluster 1 and the extremely long durations of Cluster 2.
