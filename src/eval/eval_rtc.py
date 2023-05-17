import re

arrivalTime_pattern = r'"arrivalTimeMs":(\d+)'
payloadSize_pattern = r'"payloadSize":(\d+)'
lossRates_pattern   = r'"lossRates":(\d+)'

# 读取webrtc.log文件
with open("assets/webrtc.log", "r") as file:
    log_data = file.read()

# 到达时间和payload
arrivalTimes = re.findall(arrivalTime_pattern, log_data)
payloadSizes = re.findall(payloadSize_pattern, log_data)
lossRates    = re.findall(lossRates_pattern, log_data)

# 计算吞吐量
throughput_values = []
for i in range(len(arrivalTimes) - 1):
    arrival_time1, payload_size1 = arrivalTimes[i], payloadSizes[i]
    arrival_time2, payload_size2 = arrivalTimes[i+1], payloadSizes[i+1]
    arrival_time_diff = int(arrival_time2) - int(arrival_time1)
    if arrival_time_diff == 0:
        arrival_time_diff = float(0.1)
    payload_size = int(payload_size2)
    throughput = payload_size / arrival_time_diff
    throughput_values.append(throughput)

for i in range(len(lossRates)):
    lossRates[i] = int(lossRates[i])

# 打印吞吐量
#print("吞吐量:")
#for value in throughput_values:
#    print(value, "bytes/ms")

print("Average throughput = ", sum(throughput_values) / len(throughput_values) * 1000, "bps")
print("Average loss_rate  = ", sum(lossRates) / len(lossRates))