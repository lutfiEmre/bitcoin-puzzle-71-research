from ecdsa import SigningKey, SECP256k1
import hashlib
import base58

private_key_hex = (
    "000000000000000000000000000000000000000000000072ee674e3a0b248c61"
)

private_key = bytes.fromhex(private_key_hex)
signing_key = SigningKey.from_string(private_key, curve=SECP256k1)

point = signing_key.verifying_key.pubkey.point
x = point.x()
y = point.y()

# Compressed public key:
# y çiftse 02, tekse 03
prefix = b"\x02" if y % 2 == 0 else b"\x03"
public_key = prefix + x.to_bytes(32, "big")

sha256 = hashlib.sha256(public_key).digest()
ripemd160 = hashlib.new("ripemd160", sha256).digest()

payload = b"\x00" + ripemd160
checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

address = base58.b58encode(payload + checksum).decode()

print("Compressed address:", address)