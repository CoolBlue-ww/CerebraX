import requests
import base64


def ocr_request(image_path, api_url="http://localhost:8080/layout-parsing"):
    with open(image_path, "rb") as file:
        image_bytes = file.read()
    image_data = base64.b64encode(image_bytes).decode("ascii")

    payload = {
        "file": image_data,
        "fileType": 1,
        "promptLabel": "table",
        "useLayoutDetection": False
    }

    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = ocr_request("/home/ckr-ubuntu/桌面/MyProject/CerebraX/src/cerebrax/utils/20251225170100222866.png")
    print(result)
