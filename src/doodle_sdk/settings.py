import re

def translate_channel_frequency_response(response: dict):
    interface_info = response['result'][1]['stdout']
    match = re.search(r"channel (\d+) \(([\d]+) MHz\), width: (\d+) MHz", interface_info)

    if match:
        channel = match.group(1)
        frequency = match.group(2)
        width = match.group(3)
    else:
        print("Channel, frequency, and width information not found.")

    return int(channel), int(frequency), int(width)
