from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import time

from flask import Flask, abort, jsonify, render_template, request

from challenges import get_answers, get_challenge, list_challenges


app = Flask(__name__)

_BASE_DIR = Path(__file__).resolve().parent


def _compute_static_version() -> str:
    candidates = [
        _BASE_DIR / "static" / "styles.css",
        _BASE_DIR / "static" / "app.js",
        _BASE_DIR / "static" / "padding_oracle_demo.js",
        _BASE_DIR / "static" / "fwdsec_logo.jpeg",
        _BASE_DIR / "static" / "safe-logo-lg.png",
    ]
    try:
        mtimes = [p.stat().st_mtime for p in candidates if p.exists()]
        if not mtimes:
            return str(int(time.time()))
        return str(int(max(mtimes)))
    except Exception:
        return str(int(time.time()))


_STATIC_VERSION = _compute_static_version()


@app.context_processor
def _inject_static_version():
    return {"static_version": _STATIC_VERSION}

_PADDING_ORACLE_KEY = bytes.fromhex(
    "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
)


def _po_crypto():
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad

    return AES, pad, unpad


def _po_split_token(token: str) -> tuple[bytes, bytes]:
    raw = base64.b64decode(token.strip(), validate=True)
    if len(raw) < 32:
        raise ValueError("token too short")
    iv, ct = raw[:16], raw[16:]
    if len(ct) == 0 or (len(ct) % 16) != 0:
        raise ValueError("invalid ct length")
    return iv, ct


@app.get("/")
def index():
    challenges = list_challenges()
    if not challenges:
        abort(500, description="No challenges configured")

    initial_id = challenges[0]["id"]
    initial = get_challenge(initial_id)
    if initial is None:
        abort(500, description="Initial challenge missing")

    return render_template(
        "index.html",
        challenges=challenges,
        initial_challenge=initial,
    )


@app.get("/api/challenges")
def api_list_challenges():
    return jsonify(list_challenges())


@app.get("/api/challenges/<int:challenge_id>")
def api_get_challenge(challenge_id: int):
    challenge = get_challenge(challenge_id)
    if challenge is None:
        abort(404)
    return jsonify(challenge)


def _reveal_enabled() -> bool:
    v = request.args.get("reveal", "").strip().lower()
    return v in {"1", "true", "yes", "on"}


@app.get("/api/challenges/<int:challenge_id>/answers")
def api_get_challenge_answers(challenge_id: int):
    if not _reveal_enabled():
        abort(404)

    answers = get_answers(challenge_id)
    if answers is None:
        abort(404)

    return jsonify(answers)


@app.get("/demo/padding-oracle")
def demo_padding_oracle():
    crypto_ok = True
    try:
        _po_crypto()
    except Exception:
        crypto_ok = False

    return render_template("padding_oracle_demo.html", crypto_ok=crypto_ok)


@app.post("/demo/padding-oracle/mint")
def demo_padding_oracle_mint():
    try:
        AES, pad, _unpad = _po_crypto()
    except Exception as err:
        return (f"Missing dependency for demo: {err}", 500)

    body = request.get_json(force=True) or {}
    data = body.get("data")
    payload = body.get("payload")

    if data is None and isinstance(payload, str) and payload.strip():
        try:
            data = json.loads(payload)
        except Exception:
            return jsonify(error="payload must be valid JSON"), 400

    if data is None:
        data = {"user": "bob"}

    if not isinstance(data, dict):
        return jsonify(error="data must be a JSON object"), 400

    plaintext = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    pt = plaintext.encode("utf-8")
    padded = pad(pt, 16)

    iv = os.urandom(16)
    cipher = AES.new(_PADDING_ORACLE_KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(padded)

    token = base64.b64encode(iv + ct).decode("ascii")

    ciphertext_blocks_hex = [ct[i : i + 16].hex() for i in range(0, len(ct), 16)]
    plaintext_blocks_hex = [padded[i : i + 16].hex() for i in range(0, len(padded), 16)]

    return jsonify(
        token=token,
        plaintext=plaintext,
        block_size=16,
        iv_hex=iv.hex(),
        ct_hex=ct.hex(),
        ciphertext_blocks_hex=ciphertext_blocks_hex,
        plaintext_padded_hex=padded.hex(),
        plaintext_blocks_hex=plaintext_blocks_hex,
    )


@app.post("/demo/padding-oracle/validate")
def demo_padding_oracle_validate():
    try:
        AES, _pad, unpad = _po_crypto()
    except Exception as err:
        return (f"Missing dependency for demo: {err}", 500)

    body = request.get_json(force=True) or {}
    token = str(body.get("token", ""))

    try:
        iv, ct = _po_split_token(token)
    except Exception:
        return ("Invalid token", 401)

    cipher = AES.new(_PADDING_ORACLE_KEY, AES.MODE_CBC, iv)
    padded = cipher.decrypt(ct)

    try:
        pt_bytes = unpad(padded, 16)
    except ValueError:
        return ("Bad padding", 400)
    except Exception:
        return ("Invalid token", 401)

    try:
        plaintext = pt_bytes.decode("utf-8")
        data = json.loads(plaintext)
        return jsonify(ok=True, user=data.get("user"))
    except Exception:
        return ("Invalid token", 401)


if __name__ == "__main__":
    app.run(debug=True, port=8000)

