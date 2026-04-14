import urllib.request
import os
import json

file_path = r'C:\Users\kamal\Downloads\resume (3).pdf'
filename = os.path.basename(file_path)
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
    f'Content-Type: application/pdf\r\n\r\n'
).encode('utf-8') + open(file_path, 'rb').read() + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8000/resume/upload',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        print(json.dumps(json.loads(response.read()), indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
