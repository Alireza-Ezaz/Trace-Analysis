# using babeltrace2 to parse lttng trace
import bt2

# Create a list of system calls.
system_calls = []

# Create a trace collection message iterator from our lttng trace using babeltrace2.
message_iterator = bt2.TraceCollectionMessageIterator("venv/traces/kernel")

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

print(system_call_durations)
print()
print("*****************************************************")
print()
print("Number of system calls: " + str(len(system_call_durations)))
print("Duration is in nanoseconds")

# finding some statistics

