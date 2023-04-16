import requests
import sys

# 填入你的 API Token
token = "V3tuAdSuyC6M5Rerob4vxbHRhYt3qKiZ"

# 获取账号下所有图片 hash
list_url = "https://sm.ms/api/v2/upload_history"
headers = {
    "User-Agent"   : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/80.0.3987.149 Safari/537.36",
    "Authorization": token
}

response = requests.get(list_url, headers=headers)
images = response.json()["data"]
hash_values = [image["hash"] for image in images]

# 遍历 hash 值，发送删除请求
for hash_value in hash_values:
    delete_url = "https://sm.ms/api/v2/delete/" + hash_value
    response = requests.get(delete_url, headers=headers)
    try:
        print(response.json()["message"])
    except Exception as e:
        print(e)
        sys.exit(0)
