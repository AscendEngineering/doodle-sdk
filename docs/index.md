## Project layout

Welcome to the Doodle SDK documentation. This guide will help you get started with the Doodle SDK and provide comprehensive information about its features and usage.

> **Note:** For more information on Doodle Radios, visit [Doodle's Website](https://doodlelabs.com/).

### Usage

Here is a basic example of how to use the Doodle SDK:

``` 
from doodle_sdk import Doodle

# Create an instance of the Doodle class
doodle = Doodle(ip="192.168.1.1", user="admin", password="password")

# Connect to the Doodle
if doodle.connect():
    print("Connected successfully!")
else:
    print("Failed to connect.")

```


