from __future__ import annotations

from textwrap import dedent
from typing import Any


_CHALLENGES: dict[int, dict[str, Any]] = {
    1: {
        "id": 1,
        "title": "Fetch + callback endpoint",
        "description": (
            "This endpoint accepts JSON with a URL to fetch and a callback URL to POST the fetched body to. "
            "Review it like a real code review: identify security risks, reliability issues, and how you would fix them."
        ),
        "snippets": {
            "python": dedent(
                """
                import requests, json
                from flask import Flask, request

                app = Flask(__name__)

                @app.route("/fetch", methods=["POST"])
                def fetch():
                    j = request.get_json(force=True)
                    target   = j.get("url")
                    callback = j.get("callback")
                    body = requests.get(target, timeout=3).content
                    requests.post(callback, data=body, timeout=3)
                    return "done"

                if __name__ == "__main__":
                    app.run(port=8000)
                """
            ).strip(),
            "typescript": dedent(
                """
                import express from "express";
                import axios from "axios";

                const app = express();
                app.use(express.json());

                app.post("/fetch", async (req, res) => {
                  const target = req.body?.url;
                  const callback = req.body?.callback;

                  const body = (
                    await axios.get(target, { timeout: 3000, responseType: "arraybuffer" })
                  ).data;
                  await axios.post(callback, body, { timeout: 3000 });

                  res.send("done");
                });

                app.listen(8000, () => {
                  console.log("listening on http://localhost:8000");
                });
                """
            ).strip(),
            "java": dedent(
                """
                import org.springframework.boot.SpringApplication;
                import org.springframework.boot.autoconfigure.SpringBootApplication;
                import org.springframework.http.ResponseEntity;
                import org.springframework.web.bind.annotation.PostMapping;
                import org.springframework.web.bind.annotation.RequestBody;
                import org.springframework.web.bind.annotation.RestController;
                import org.springframework.web.client.RestTemplate;

                import java.util.Map;

                @SpringBootApplication
                @RestController
                public class App {
                  private final RestTemplate http = new RestTemplate();

                  @PostMapping("/fetch")
                  public ResponseEntity<String> fetch(@RequestBody Map<String, String> j) {
                    String target = j.get("url");
                    String callback = j.get("callback");

                    byte[] body = http.getForObject(target, byte[].class);
                    http.postForEntity(callback, body, Void.class);

                    return ResponseEntity.ok("done");
                  }

                  public static void main(String[] args) {
                    SpringApplication.run(App.class, args);
                  }
                }
                """
            ).strip(),
            "cpp": dedent(
                """
                #include <cpr/cpr.h>
                #include <httplib.h>
                #include <nlohmann/json.hpp>

                using json = nlohmann::json;

                int main() {
                  httplib::Server app;

                  app.Post("/fetch", [](const httplib::Request& req, httplib::Response& res) {
                    auto j = json::parse(req.body);
                    std::string target = j.value("url", "");
                    std::string callback = j.value("callback", "");

                    auto body = cpr::Get(cpr::Url{target}, cpr::Timeout{3000}).text;
                    cpr::Post(cpr::Url{callback}, cpr::Body{body}, cpr::Timeout{3000});

                    res.set_content("done", "text/plain");
                  });

                  app.listen("0.0.0.0", 8000);
                }
                """
            ).strip(),
        },
    },
    2: {
        "id": 2,
        "title": "JWT auth endpoints",
        "description": (
            "A small API that issues JWTs on login and protects routes using the Authorization header. "
            "Review it like a real code review: security, correctness, and operational safety."
        ),
        "snippets": {
            "typescript": dedent(
                """
                import express from "express";
                import bodyParser from "body-parser";
                import jwt from "jsonwebtoken";
                import users from "./users";

                const app = express();
                app.use(bodyParser.json());

                const SECRET_KEY = "mysecretkey";

                app.post("/login", (req, res) => {
                  const { username, password } = req.body;

                  if (users.checkCredentials(username, password)) {
                    const token = jwt.sign({ username: username }, SECRET_KEY);
                    res.json({ token: token });
                  } else {
                    res.status(401).send("Unauthorized");
                  }
                });

                app.get("/protected", (req, res) => {
                  const token = req.headers.authorization?.split(" ")[1];

                  try {
                    const decoded = jwt.verify(token, SECRET_KEY) as any;
                    res.json({ message: `Welcome ${decoded.username}!` });
                  } catch (err) {
                    console.error(err);
                    res.status(401).send("Unauthorized");
                  }
                });

                app.get("/admin", (req, res) => {
                  const token = req.headers.authorization?.split(" ")[1];

                  try {
                    const decoded = jwt.verify(token, SECRET_KEY) as any;
                    res.json({ message: `Welcome ${decoded.username}!` });
                  } catch (err) {
                    console.error(err);
                    res.status(401).send("Unauthorized");
                  }
                });

                const PORT = process.env.PORT || 80;
                app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
                """
            ).strip(),
            "python": dedent(
                """
                import os

                import jwt
                from flask import Flask, jsonify, request

                app = Flask(__name__)

                SECRET_KEY = "mysecretkey"


                def check_credentials(username: str | None, password: str | None) -> bool:
                    return username == "admin" and password == "admin"


                @app.post("/login")
                def login():
                    body = request.get_json(force=True)
                    username = body.get("username")
                    password = body.get("password")

                    if check_credentials(username, password):
                        token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
                        return jsonify({"token": token})

                    return ("Unauthorized", 401)


                @app.get("/protected")
                def protected():
                    auth = request.headers.get("Authorization")
                    token = auth.split(" ")[1] if auth else None

                    try:
                        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                        return jsonify({"message": f"Welcome {decoded['username']}!"})
                    except Exception as err:
                        return (str(err), 401)


                @app.get("/admin")
                def admin():
                    auth = request.headers.get("Authorization")
                    token = auth.split(" ")[1] if auth else None

                    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                    return jsonify({"message": f"Welcome {decoded['username']}!"})


                if __name__ == "__main__":
                    port = int(os.environ.get("PORT", "80"))
                    app.run(host="0.0.0.0", port=port)
                """
            ).strip(),
            "java": dedent(
                """
                import com.auth0.jwt.JWT;
                import com.auth0.jwt.algorithms.Algorithm;
                import com.auth0.jwt.exceptions.JWTVerificationException;
                import com.auth0.jwt.interfaces.DecodedJWT;
                import com.auth0.jwt.interfaces.JWTVerifier;
                import org.springframework.boot.SpringApplication;
                import org.springframework.boot.autoconfigure.SpringBootApplication;
                import org.springframework.http.ResponseEntity;
                import org.springframework.web.bind.annotation.GetMapping;
                import org.springframework.web.bind.annotation.PostMapping;
                import org.springframework.web.bind.annotation.RequestBody;
                import org.springframework.web.bind.annotation.RequestHeader;
                import org.springframework.web.bind.annotation.RestController;

                import java.util.Map;

                @SpringBootApplication
                @RestController
                public class App {
                  private static final String SECRET_KEY = "mysecretkey";
                  private static final Algorithm ALG = Algorithm.HMAC256(SECRET_KEY);
                  private static final JWTVerifier VERIFIER = JWT.require(ALG).build();

                  private boolean checkCredentials(String username, String password) {
                    return "admin".equals(username) && "admin".equals(password);
                  }

                  @PostMapping("/login")
                  public ResponseEntity<?> login(@RequestBody Map<String, String> body) {
                    String username = body.get("username");
                    String password = body.get("password");

                    if (!checkCredentials(username, password)) {
                      return ResponseEntity.status(401).body("Unauthorized");
                    }

                    String token = JWT.create()
                        .withClaim("username", username)
                        .sign(ALG);

                    return ResponseEntity.ok(Map.of("token", token));
                  }

                  @GetMapping("/protected")
                  public ResponseEntity<?> protectedRoute(@RequestHeader(value = "Authorization", required = false) String auth) {
                    String token = auth != null ? auth.split(" ")[1] : null;

                    try {
                      DecodedJWT decoded = VERIFIER.verify(token);
                      return ResponseEntity.ok(Map.of("message", "Welcome " + decoded.getClaim("username").asString() + "!"));
                    } catch (JWTVerificationException ex) {
                      return ResponseEntity.status(401).body(ex.getMessage());
                    }
                  }

                  @GetMapping("/admin")
                  public ResponseEntity<?> admin(@RequestHeader(value = "Authorization", required = false) String auth) {
                    String token = auth != null ? auth.split(" ")[1] : null;

                    try {
                      DecodedJWT decoded = VERIFIER.verify(token);
                      return ResponseEntity.ok(Map.of("message", "Welcome " + decoded.getClaim("username").asString() + "!"));
                    } catch (JWTVerificationException ex) {
                      return ResponseEntity.status(401).body("Unauthorized");
                    }
                  }

                  public static void main(String[] args) {
                    String port = System.getenv().getOrDefault("PORT", "80");
                    System.setProperty("server.port", port);
                    SpringApplication.run(App.class, args);
                  }
                }
                """
            ).strip(),
            "cpp": dedent(
                """
                #include <httplib.h>
                #include <jwt-cpp/jwt.h>
                #include <nlohmann/json.hpp>

                using json = nlohmann::json;

                static const std::string SECRET_KEY = "mysecretkey";

                static bool checkCredentials(const std::string& username, const std::string& password) {
                  return username == "admin" && password == "admin";
                }

                static std::string bearerToken(const httplib::Request& req) {
                  auto auth = req.get_header_value("Authorization");
                  auto pos = auth.find(' ');
                  if (pos == std::string::npos) return "";
                  return auth.substr(pos + 1);
                }

                int main() {
                  httplib::Server app;

                  app.Post("/login", [](const httplib::Request& req, httplib::Response& res) {
                    auto body = json::parse(req.body);
                    std::string username = body.value("username", "");
                    std::string password = body.value("password", "");

                    if (!checkCredentials(username, password)) {
                      res.status = 401;
                      res.set_content("Unauthorized", "text/plain");
                      return;
                    }

                    auto token = jwt::create()
                        .set_payload_claim("username", jwt::claim(username))
                        .sign(jwt::algorithm::hs256{SECRET_KEY});

                    res.set_content(json{{"token", token}}.dump(), "application/json");
                  });

                  app.Get("/protected", [](const httplib::Request& req, httplib::Response& res) {
                    auto token = bearerToken(req);

                    try {
                      auto decoded = jwt::decode(token);
                      jwt::verify().allow_algorithm(jwt::algorithm::hs256{SECRET_KEY}).verify(decoded);
                      auto username = decoded.get_payload_claim("username").as_string();
                      res.set_content(json{{"message", "Welcome " + username + "!"}}.dump(), "application/json");
                    } catch (const std::exception& err) {
                      res.status = 401;
                      res.set_content(err.what(), "text/plain");
                    }
                  });

                  app.Get("/admin", [](const httplib::Request& req, httplib::Response& res) {
                    auto token = bearerToken(req);

                    try {
                      auto decoded = jwt::decode(token);
                      jwt::verify().allow_algorithm(jwt::algorithm::hs256{SECRET_KEY}).verify(decoded);
                      auto username = decoded.get_payload_claim("username").as_string();
                      res.set_content(json{{"message", "Welcome " + username + "!"}}.dump(), "application/json");
                    } catch (...) {
                      res.status = 401;
                      res.set_content("Unauthorized", "text/plain");
                    }
                  });

                  app.listen("0.0.0.0", 80);
                }
                """
            ).strip(),
        },
    },
    3: {
        "id": 3,
        "title": "Login",
        "description": (
            "A login page accepts a `next` URL and redirects to it after creating a session. "
            "Review it like a real code review: web security and correctness."
        ),
        "snippets": {
            "typescript": dedent(
                """
                import express from "express";

                const app = express();
                app.use(express.urlencoded({ extended: false }));

                function escapeAttr(str = ""): string {
                  return str
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")
                    .replace(/"/g, "&quot;")
                    .replace(/'/g, "&#39;");
                }

                app.get("/login", (req, res) => {
                  const next = (req.query.next as string) || "/";
                  const safeValue = escapeAttr(next);

                  res.send(`
                    <!doctype html>
                    <html>
                      <body>
                        <h1>Please sign in</h1>
                        <form action="/session" method="post">
                          <input type="hidden" name="next" value="${safeValue}">
                          <button>Login</button>
                        </form>
                      </body>
                    </html>
                  `);
                });

                app.post("/session", (req, res) => {
                  res.redirect(req.body.next);
                });

                app.listen(3000, () => console.log("demo on :3000"));
                """
            ).strip(),
            "python": dedent(
                """
                from flask import Flask, redirect, request

                app = Flask(__name__)


                def escape_attr(s: str = "") -> str:
                    return (
                        s.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace('"', "&quot;")
                        .replace("'", "&#39;")
                    )


                @app.get("/login")
                def login():
                    next_url = request.args.get("next") or "/"
                    safe_value = escape_attr(next_url)

                    return f'''
                <!doctype html>
                <html>
                  <body>
                    <h1>Please sign in</h1>
                    <form action="/session" method="post">
                      <input type="hidden" name="next" value="{safe_value}">
                      <button>Login</button>
                    </form>
                  </body>
                </html>
                '''.strip()


                @app.post("/session")
                def session():
                    return redirect(request.form.get("next"))


                if __name__ == "__main__":
                    app.run(port=3000, debug=True)
                """
            ).strip(),
            "java": dedent(
                """
                import org.springframework.boot.SpringApplication;
                import org.springframework.boot.autoconfigure.SpringBootApplication;
                import org.springframework.http.HttpHeaders;
                import org.springframework.http.ResponseEntity;
                import org.springframework.web.bind.annotation.GetMapping;
                import org.springframework.web.bind.annotation.PostMapping;
                import org.springframework.web.bind.annotation.RequestParam;
                import org.springframework.web.bind.annotation.RestController;

                @SpringBootApplication
                @RestController
                public class App {
                  private String escapeAttr(String s) {
                    if (s == null) return "";
                    return s
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\\\"", "&quot;")
                        .replace("'", "&#39;");
                  }

                  @GetMapping("/login")
                  public ResponseEntity<String> login(@RequestParam(value = "next", required = false) String next) {
                    String nextUrl = (next == null || next.isEmpty()) ? "/" : next;
                    String safeValue = escapeAttr(nextUrl);

                    String html =
                        "<!doctype html>\\n" +
                        "<html>\\n" +
                        "  <body>\\n" +
                        "    <h1>Please sign in</h1>\\n" +
                        "    <form action='/session' method='post'>\\n" +
                        "      <input type='hidden' name='next' value='" + safeValue + "'>\\n" +
                        "      <button>Login</button>\\n" +
                        "    </form>\\n" +
                        "  </body>\\n" +
                        "</html>\\n";

                    return ResponseEntity.ok(html);
                  }

                  @PostMapping("/session")
                  public ResponseEntity<Void> session(@RequestParam(value = "next", required = false) String next) {
                    return ResponseEntity.status(302).header(HttpHeaders.LOCATION, next).build();
                  }

                  public static void main(String[] args) {
                    SpringApplication.run(App.class, args);
                  }
                }
                """
            ).strip(),
            "cpp": dedent(
                """
                #include <httplib.h>
                #include <string>

                static void replaceAll(std::string& s, const std::string& from, const std::string& to) {
                  size_t start = 0;
                  while ((start = s.find(from, start)) != std::string::npos) {
                    s.replace(start, from.length(), to);
                    start += to.length();
                  }
                }

                static std::string escapeAttr(std::string s) {
                  replaceAll(s, "&", "&amp;");
                  replaceAll(s, "<", "&lt;");
                  replaceAll(s, ">", "&gt;");
                  replaceAll(s, "\\\"", "&quot;");
                  replaceAll(s, "'", "&#39;");
                  return s;
                }

                int main() {
                  httplib::Server app;

                  app.Get("/login", [](const httplib::Request& req, httplib::Response& res) {
                    std::string next = "/";
                    if (req.has_param("next")) next = req.get_param_value("next");
                    auto safeValue = escapeAttr(next);

                    std::string html =
                      "<!doctype html>\\n"
                      "<html>\\n"
                      "  <body>\\n"
                      "    <h1>Please sign in</h1>\\n"
                      "    <form action=\\"/session\\" method=\\"post\\">\\n"
                      "      <input type=\\"hidden\\" name=\\"next\\" value=\\"" + safeValue + "\\">\\n"
                      "      <button>Login</button>\\n"
                      "    </form>\\n"
                      "  </body>\\n"
                      "</html>\\n";

                    res.set_content(html, "text/html");
                  });

                  app.Post("/session", [](const httplib::Request& req, httplib::Response& res) {
                    auto next = req.get_param_value("next");
                    res.status = 302;
                    res.set_header("Location", next);
                  });

                  app.listen("0.0.0.0", 3000);
                }
                """
            ).strip(),
        },
    },
    4: {
        "id": 4,
        "title": "Encrypted token validation",
        "description": (
            "An API decrypts an encrypted token and responds differently depending on why validation failed. "
            "Review it like a real code review: cryptography, error handling, and web security."
        ),
        "snippets": {
            "typescript": dedent(
                """
                import crypto from "crypto";
                import express from "express";

                const app = express();
                app.use(express.json());

                const KEY = Buffer.from(
                  "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff",
                  "hex"
                );

                function decryptToken(token: string): string {
                  const raw = Buffer.from(token, "base64");
                  const iv = raw.subarray(0, 16);
                  const ct = raw.subarray(16);

                  const decipher = crypto.createDecipheriv("aes-256-cbc", KEY, iv);
                  const pt = Buffer.concat([decipher.update(ct), decipher.final()]);
                  return pt.toString("utf8");
                }

                app.post("/validate", (req, res) => {
                  const token = String(req.body.token || "");

                  try {
                    const plaintext = decryptToken(token);
                    const data = JSON.parse(plaintext);
                    return res.json({ ok: true, user: data.user });
                  } catch (err: any) {
                    const msg = String(err?.message || "");
                    if (msg.includes("bad decrypt") || msg.includes("wrong final block length")) {
                      return res.status(400).send("Bad padding");
                    }
                    return res.status(401).send("Invalid token");
                  }
                });

                app.listen(3000);
                """
            ).strip(),
            "python": dedent(
                """
                import base64
                import json

                from Crypto.Cipher import AES
                from Crypto.Util.Padding import unpad
                from flask import Flask, jsonify, request

                app = Flask(__name__)

                KEY = bytes.fromhex(
                    "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
                )


                def decrypt_token(token: str) -> str:
                    raw = base64.b64decode(token)
                    iv, ct = raw[:16], raw[16:]

                    cipher = AES.new(KEY, AES.MODE_CBC, iv)
                    padded = cipher.decrypt(ct)
                    pt = unpad(padded, 16)
                    return pt.decode("utf-8")


                @app.post("/validate")
                def validate():
                    body = request.get_json(force=True) or {}
                    token = body.get("token", "")

                    try:
                        plaintext = decrypt_token(token)
                        data = json.loads(plaintext)
                        return jsonify(ok=True, user=data.get("user"))
                    except ValueError:
                        return ("Bad padding", 400)
                    except Exception:
                        return ("Invalid token", 401)


                if __name__ == "__main__":
                    app.run(port=3000)
                """
            ).strip(),
            "java": dedent(
                """
                import com.fasterxml.jackson.databind.JsonNode;
                import com.fasterxml.jackson.databind.ObjectMapper;
                import org.springframework.boot.SpringApplication;
                import org.springframework.boot.autoconfigure.SpringBootApplication;
                import org.springframework.http.ResponseEntity;
                import org.springframework.web.bind.annotation.PostMapping;
                import org.springframework.web.bind.annotation.RequestBody;
                import org.springframework.web.bind.annotation.RestController;

                import javax.crypto.BadPaddingException;
                import javax.crypto.Cipher;
                import javax.crypto.spec.IvParameterSpec;
                import javax.crypto.spec.SecretKeySpec;
                import java.nio.charset.StandardCharsets;
                import java.util.Arrays;
                import java.util.Base64;
                import java.util.Map;

                @SpringBootApplication
                @RestController
                public class App {
                  private static final ObjectMapper JSON = new ObjectMapper();
                  private static final byte[] KEY = hex("00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff");

                  private static byte[] hex(String s) {
                    int len = s.length();
                    byte[] out = new byte[len / 2];
                    for (int i = 0; i < len; i += 2) {
                      out[i / 2] = (byte) Integer.parseInt(s.substring(i, i + 2), 16);
                    }
                    return out;
                  }

                  private static String decryptToken(String token) throws Exception {
                    byte[] raw = Base64.getDecoder().decode(token);
                    byte[] iv = Arrays.copyOfRange(raw, 0, 16);
                    byte[] ct = Arrays.copyOfRange(raw, 16, raw.length);

                    Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
                    cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(KEY, "AES"), new IvParameterSpec(iv));
                    byte[] pt = cipher.doFinal(ct);
                    return new String(pt, StandardCharsets.UTF_8);
                  }

                  @PostMapping("/validate")
                  public ResponseEntity<?> validate(@RequestBody Map<String, Object> body) {
                    String token = String.valueOf(body.getOrDefault("token", ""));

                    try {
                      String plaintext = decryptToken(token);
                      JsonNode node = JSON.readTree(plaintext);
                      return ResponseEntity.ok(Map.of("ok", true, "user", node.path("user").asText()));
                    } catch (BadPaddingException ex) {
                      return ResponseEntity.status(400).body("Bad padding");
                    } catch (Exception ex) {
                      return ResponseEntity.status(401).body("Invalid token");
                    }
                  }

                  public static void main(String[] args) {
                    SpringApplication.run(App.class, args);
                  }
                }
                """
            ).strip(),
            "cpp": dedent(
                """
                #include <cstring>
                #include <stdexcept>
                #include <string>
                #include <vector>

                #include <httplib.h>
                #include <nlohmann/json.hpp>
                #include <openssl/bio.h>
                #include <openssl/buffer.h>
                #include <openssl/evp.h>

                using json = nlohmann::json;

                static const std::string KEY = "0123456789abcdef0123456789abcdef";

                static std::vector<unsigned char> base64Decode(const std::string& in) {
                  BIO* b64 = BIO_new(BIO_f_base64());
                  BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
                  BIO* bio = BIO_new_mem_buf(in.data(), static_cast<int>(in.size()));
                  bio = BIO_push(b64, bio);

                  std::vector<unsigned char> out(in.size());
                  int len = BIO_read(bio, out.data(), static_cast<int>(out.size()));
                  BIO_free_all(bio);
                  if (len <= 0) throw std::runtime_error("invalid token");
                  out.resize(static_cast<size_t>(len));
                  return out;
                }

                static std::string decryptToken(const std::string& token) {
                  auto raw = base64Decode(token);
                  if (raw.size() < 17) throw std::runtime_error("invalid token");

                  unsigned char iv[16];
                  std::memcpy(iv, raw.data(), 16);
                  const unsigned char* ct = raw.data() + 16;
                  int ctLen = static_cast<int>(raw.size() - 16);

                  EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
                  std::vector<unsigned char> pt(static_cast<size_t>(ctLen) + 16);
                  int outLen1 = 0;
                  int outLen2 = 0;

                  EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr,
                                     reinterpret_cast<const unsigned char*>(KEY.data()), iv);
                  if (EVP_DecryptUpdate(ctx, pt.data(), &outLen1, ct, ctLen) != 1) {
                    EVP_CIPHER_CTX_free(ctx);
                    throw std::runtime_error("invalid token");
                  }
                  if (EVP_DecryptFinal_ex(ctx, pt.data() + outLen1, &outLen2) != 1) {
                    EVP_CIPHER_CTX_free(ctx);
                    throw std::runtime_error("bad padding");
                  }

                  EVP_CIPHER_CTX_free(ctx);
                  return std::string(reinterpret_cast<char*>(pt.data()), static_cast<size_t>(outLen1 + outLen2));
                }

                int main() {
                  httplib::Server app;

                  app.Post("/validate", [](const httplib::Request& req, httplib::Response& res) {
                    auto body = json::parse(req.body);
                    std::string token = body.value("token", "");

                    try {
                      auto plaintext = decryptToken(token);
                      auto data = json::parse(plaintext);
                      res.set_content(json{{"ok", true}, {"user", data.value("user", "")}}.dump(), "application/json");
                    } catch (const std::runtime_error& err) {
                      if (std::string(err.what()) == "bad padding") {
                        res.status = 400;
                        res.set_content("Bad padding", "text/plain");
                      } else {
                        res.status = 401;
                        res.set_content("Invalid token", "text/plain");
                      }
                    } catch (...) {
                      res.status = 401;
                      res.set_content("Invalid token", "text/plain");
                    }
                  });

                  app.listen("0.0.0.0", 3000);
                }
                """
            ).strip(),
        },
    },
}


def list_challenges() -> list[dict[str, Any]]:
    return [{"id": c["id"], "title": c["title"]} for _, c in sorted(_CHALLENGES.items())]


def get_challenge(challenge_id: int) -> dict[str, Any] | None:
    return _CHALLENGES.get(challenge_id)


_ANSWERS: dict[int, dict[str, Any]] = {
    1: {
        "id": 1,
        "languages": {
            "python": [
                {
                    "id": "ssrf",
                    "title": "Server-Side Request Forgery (SSRF)",
                    "problem": "The server fetches a user-controlled URL, which can be used to reach internal services and metadata endpoints.",
                    "fix": "Validate/allowlist destinations (scheme/host/port), block private IP ranges, and use an egress proxy with policy.",
                    "lines": [9, 11],
                },
                {
                    "id": "callback-exfil",
                    "title": "User-controlled callback (exfiltration)",
                    "problem": "The server POSTs the fetched body to a user-controlled callback, enabling data exfiltration and internal pivoting.",
                    "fix": "Remove callbacks or restrict them to trusted origins; consider returning the result directly to the caller.",
                    "lines": [10, 12],
                },
                {
                    "id": "forced-json",
                    "title": "Forced JSON parsing",
                    "problem": "Forcing JSON parsing can accept unexpected content-types and bypass input validation expectations.",
                    "fix": "Require `Content-Type: application/json` and validate a strict request schema.",
                    "lines": [8],
                },
                {
                    "id": "no-auth",
                    "title": "No authentication / abuse controls",
                    "problem": "Anyone can use the endpoint as an open proxy to fetch arbitrary content.",
                    "fix": "Add authn/authz and abuse controls (rate limiting, quotas, audit logs).",
                    "lines": [6],
                },
                {
                    "id": "no-error-handling",
                    "title": "No error handling",
                    "problem": "Network failures and invalid URLs can raise exceptions and cause 500s or partial failures.",
                    "fix": "Handle errors explicitly, return structured errors, and implement retries/backoff where appropriate.",
                    "lines": [11, 12],
                },
                {
                    "id": "unbounded-response",
                    "title": "Unbounded response size in memory",
                    "problem": "Fetching `.content` reads the entire response into memory, enabling memory pressure and DoS.",
                    "fix": "Stream responses, enforce size limits, and set stricter timeouts.",
                    "lines": [11],
                },
            ],
            "typescript": [
                {
                    "id": "ssrf",
                    "title": "Server-Side Request Forgery (SSRF)",
                    "problem": "The server fetches a user-controlled URL, which can be used to reach internal services and metadata endpoints.",
                    "fix": "Validate/allowlist destinations and block private IP ranges; consider an egress proxy.",
                    "lines": [8, 12],
                },
                {
                    "id": "callback-exfil",
                    "title": "User-controlled callback (exfiltration)",
                    "problem": "The server POSTs the fetched body to a user-controlled callback, enabling data exfiltration and internal pivoting.",
                    "fix": "Restrict callbacks to trusted origins or remove the callback mechanism entirely.",
                    "lines": [9, 14],
                },
                {
                    "id": "no-auth",
                    "title": "No authentication / abuse controls",
                    "problem": "Anyone can use the endpoint as an open proxy to fetch arbitrary content.",
                    "fix": "Add authentication and rate limiting/quotas.",
                    "lines": [7],
                },
                {
                    "id": "no-validation",
                    "title": "No URL validation",
                    "problem": "The URL inputs are not validated for scheme/host/port, enabling unsafe protocols and destinations.",
                    "fix": "Validate URLs, enforce https, and reject private/intranet ranges.",
                    "lines": [8, 9],
                },
                {
                    "id": "no-error-handling",
                    "title": "No error handling",
                    "problem": "Failures from axios will throw and may crash the request handler or return a 500.",
                    "fix": "Add try/catch, return structured errors, and consider retries/backoff.",
                    "lines": [11, 14],
                },
            ],
            "java": [
                {
                    "id": "ssrf",
                    "title": "Server-Side Request Forgery (SSRF)",
                    "problem": "The server fetches a user-controlled URL, which can be used to reach internal services and metadata endpoints.",
                    "fix": "Validate/allowlist destinations and block private IP ranges; consider an egress proxy.",
                    "lines": [18, 21],
                },
                {
                    "id": "callback-exfil",
                    "title": "User-controlled callback (exfiltration)",
                    "problem": "The server POSTs the fetched body to a user-controlled callback, enabling data exfiltration and internal pivoting.",
                    "fix": "Restrict callbacks to trusted origins or remove the callback mechanism.",
                    "lines": [19, 22],
                },
                {
                    "id": "no-auth",
                    "title": "No authentication / abuse controls",
                    "problem": "Anyone can use the endpoint as an open proxy to fetch and forward content.",
                    "fix": "Add authn/authz and rate limiting/quotas/auditing.",
                    "lines": [16],
                },
                {
                    "id": "no-error-handling",
                    "title": "No error handling",
                    "problem": "Invalid URLs and timeouts can raise exceptions and return a 500.",
                    "fix": "Catch and translate exceptions to safe error responses; set timeouts explicitly.",
                    "lines": [21, 22],
                },
            ],
            "cpp": [
                {
                    "id": "ssrf",
                    "title": "Server-Side Request Forgery (SSRF)",
                    "problem": "The server fetches a user-controlled URL, which can be used to reach internal services and metadata endpoints.",
                    "fix": "Validate/allowlist destinations and block private IP ranges; consider egress controls.",
                    "lines": [12, 15],
                },
                {
                    "id": "callback-exfil",
                    "title": "User-controlled callback (exfiltration)",
                    "problem": "The server POSTs the fetched body to a user-controlled callback, enabling data exfiltration and internal pivoting.",
                    "fix": "Restrict callbacks to trusted origins or remove the callback mechanism.",
                    "lines": [13, 16],
                },
                {
                    "id": "no-auth",
                    "title": "No authentication / abuse controls",
                    "problem": "Anyone can use the endpoint as an open proxy to fetch and forward content.",
                    "fix": "Add authentication and rate limiting/quotas/auditing.",
                    "lines": [10],
                },
                {
                    "id": "no-error-handling",
                    "title": "No error handling",
                    "problem": "Invalid inputs and network failures can throw exceptions and return a 500.",
                    "fix": "Add validation and explicit error handling with safe error responses.",
                    "lines": [11, 15, 16],
                },
            ],
        },
    },
    2: {
        "id": 2,
        "languages": {
            "typescript": [
                {
                    "id": "hardcoded-secret",
                    "title": "Hard-coded JWT secret",
                    "problem": 'const SECRET_KEY = "mysecretkey" exposes credentials to anyone with code access.',
                    "fix": "Load from an environment variable or secrets manager and rotate regularly.",
                    "lines": [9],
                },
                {
                    "id": "weak-secret",
                    "title": "Weak / short secret value",
                    "problem": "A simple word is easy to brute-force, breaking HS256 signatures.",
                    "fix": "Use ≥ 32 random bytes (e.g., crypto.randomBytes(32).toString('hex')).",
                    "lines": [9],
                },
                {
                    "id": "no-exp",
                    "title": "Tokens never expire",
                    "problem": "The token omits an exp claim, so stolen tokens work indefinitely.",
                    "fix": "Add an expiration (e.g., expiresIn: '15m') plus a refresh-token flow.",
                    "lines": [15],
                },
                {
                    "id": "no-aud-iss",
                    "title": "No audience (aud) or issuer (iss) checks",
                    "problem": "The server will accept tokens minted for other services (confused-deputy risk).",
                    "fix": "Include aud and iss when signing and validate them during verification.",
                    "lines": [15, 26, 38],
                },
                {
                    "id": "auth-header-missing-check",
                    "title": "Missing presence check for Authorization header",
                    "problem": "Verification runs even when the header is missing or malformed, producing avoidable errors and DoS vectors.",
                    "fix": "Return 401 immediately when the header is absent or not a Bearer token.",
                    "lines": [23, 26, 35, 38],
                },
                {
                    "id": "admin-no-role-check",
                    "title": "Privilege escalation on /admin route",
                    "problem": "Any user with a valid token can hit /admin; there’s no role/claim check.",
                    "fix": "Add a role claim (e.g., role: 'admin') and enforce it; otherwise return 403.",
                    "lines": [34],
                },
                {
                    "id": "no-rate-limit",
                    "title": "No rate limiting or lockout on /login",
                    "problem": "Enables brute-force and credential-stuffing attacks.",
                    "fix": "Use middleware like express-rate-limit and track failures with backoff/lockout.",
                    "lines": [11],
                },
                {
                    "id": "plain-http",
                    "title": "Listening on plain HTTP (port 80) by default",
                    "problem": "Tokens and passwords can travel unencrypted if TLS termination isn’t in front.",
                    "fix": "Enforce HTTPS in production or redirect HTTP → HTTPS.",
                    "lines": [46, 47],
                },
                {
                    "id": "missing-security-headers",
                    "title": "Missing security headers",
                    "problem": "No CSP/HSTS/etc., increasing XSS, clickjacking, and MIME-sniffing risk.",
                    "fix": "Add Helmet and configure CSP + strict-transport-security appropriately.",
                    "lines": [6],
                },
                {
                    "id": "deprecated-body-parser",
                    "title": "Deprecated body-parsing approach",
                    "problem": "Using bodyParser.json() separately is outdated and may signal stale dependencies.",
                    "fix": "Replace with app.use(express.json()).",
                    "lines": [7],
                },
                {
                    "id": "password-policy-unclear",
                    "title": "Unclear password-handling policy",
                    "problem": "If credentials are compared as plain strings, stored passwords might be unhashed.",
                    "fix": "Store passwords with a strong hash (bcrypt/argon2) and use constant-time comparison.",
                    "lines": [14],
                },
                {
                    "id": "error-leakage",
                    "title": "Potential verbose error leakage",
                    "problem": "Logging raw errors (and/or exposing details) can leak sensitive information in production.",
                    "fix": "Sanitize logs and return generic client errors; ensure debug logs aren’t exposed.",
                    "lines": [29, 41],
                },
                {
                    "id": "jsonwebtoken-historical-caveat",
                    "title": "Historical caveat (jsonwebtoken ≤ 8.5.1)",
                    "problem": "Older versions had a flaw where a null/undefined/empty secret could effectively allow alg:none bypass.",
                    "fix": "Ensure jsonwebtoken v9+, never pass empty secrets, and restrict accepted algorithms explicitly.",
                    "lines": [26, 38],
                },
            ],
            "python": [
                {
                    "id": "hardcoded-secret",
                    "title": "Hard-coded JWT secret",
                    "problem": 'SECRET_KEY = "mysecretkey" exposes credentials to anyone with code access.',
                    "fix": "Load from an environment variable or secrets manager and rotate regularly.",
                    "lines": [8],
                },
                {
                    "id": "weak-secret",
                    "title": "Weak / short secret value",
                    "problem": "A simple word is easy to brute-force, breaking HS256 signatures.",
                    "fix": "Use ≥ 32 random bytes for HS256 keys and rotate regularly.",
                    "lines": [8],
                },
                {
                    "id": "no-exp",
                    "title": "Tokens never expire",
                    "problem": "The token omits an exp claim, so stolen tokens work indefinitely.",
                    "fix": "Add exp and enforce it; consider short-lived access tokens + refresh tokens.",
                    "lines": [22],
                },
                {
                    "id": "no-aud-iss",
                    "title": "No audience (aud) or issuer (iss) checks",
                    "problem": "The server will accept tokens minted for other services (confused-deputy risk).",
                    "fix": "Include aud/iss in the token and validate them during decoding.",
                    "lines": [22, 34, 45],
                },
                {
                    "id": "auth-header-missing-check",
                    "title": "Missing presence check for Authorization header",
                    "problem": "Decoding runs even when the header is missing or malformed, producing avoidable errors and DoS vectors.",
                    "fix": "Return 401 immediately when the header is absent or not a Bearer token.",
                    "lines": [30, 31, 34, 42, 43, 45],
                },
                {
                    "id": "admin-no-role-check",
                    "title": "Privilege escalation on /admin route",
                    "problem": "Any user with a valid token can hit /admin; there’s no role/claim check.",
                    "fix": "Add a role claim and enforce it; otherwise return 403.",
                    "lines": [40],
                },
                {
                    "id": "no-rate-limit",
                    "title": "No rate limiting or lockout on /login",
                    "problem": "Enables brute-force and credential-stuffing attacks.",
                    "fix": "Add rate limiting and track failed logins with backoff/lockout.",
                    "lines": [15],
                },
                {
                    "id": "plain-http",
                    "title": "Listening on plain HTTP (port 80) by default",
                    "problem": "Tokens and passwords can travel unencrypted if TLS termination isn’t in front.",
                    "fix": "Enforce HTTPS in production or redirect HTTP → HTTPS.",
                    "lines": [50, 51],
                },
                {
                    "id": "missing-security-headers",
                    "title": "Missing security headers",
                    "problem": "No CSP/HSTS/etc., increasing XSS/clickjacking/MIME-sniffing risk.",
                    "fix": "Set appropriate security headers (e.g., via Flask-Talisman) and enforce HSTS behind TLS.",
                    "lines": [6],
                },
                {
                    "id": "password-policy-unclear",
                    "title": "Unclear password-handling policy",
                    "problem": "Credentials appear to be compared directly, implying plaintext password handling.",
                    "fix": "Use bcrypt/argon2 hashed passwords and constant-time verification.",
                    "lines": [11, 12, 21],
                },
                {
                    "id": "error-leakage",
                    "title": "Potential verbose error leakage",
                    "problem": "Returning raw exception messages can leak sensitive details to clients.",
                    "fix": "Log safely and return only generic error messages to clients.",
                    "lines": [37],
                },
            ],
            "java": [
                {
                    "id": "hardcoded-secret",
                    "title": "Hard-coded JWT secret",
                    "problem": 'A hard-coded secret exposes credentials to anyone with code access.',
                    "fix": "Load from environment/secrets manager and rotate regularly.",
                    "lines": [20],
                },
                {
                    "id": "weak-secret",
                    "title": "Weak / short secret value",
                    "problem": "A simple word is easy to brute-force, breaking HS256 signatures.",
                    "fix": "Use a long random secret (≥ 32 bytes) and rotate regularly.",
                    "lines": [20],
                },
                {
                    "id": "no-exp",
                    "title": "Tokens never expire",
                    "problem": "The token omits an expiration, so stolen tokens work indefinitely.",
                    "fix": "Add exp and enforce it; consider short-lived access tokens + refresh tokens.",
                    "lines": [37, 38, 39],
                },
                {
                    "id": "no-aud-iss",
                    "title": "No audience (aud) or issuer (iss) checks",
                    "problem": "The server will accept tokens minted for other services (confused-deputy risk).",
                    "fix": "Include iss/aud on minting and require them in verification.",
                    "lines": [22, 37, 39, 49, 61],
                },
                {
                    "id": "auth-header-missing-check",
                    "title": "Missing presence check for Authorization header",
                    "problem": "Splitting and verification can run on missing/malformed headers, causing avoidable errors and DoS vectors.",
                    "fix": "Validate 'Authorization: Bearer <token>' format before parsing or verifying.",
                    "lines": [46, 49, 58, 61],
                },
                {
                    "id": "admin-no-role-check",
                    "title": "Privilege escalation on /admin route",
                    "problem": "Any user with a valid token can hit /admin; there’s no role/claim check.",
                    "fix": "Add a role claim and enforce it; otherwise return 403.",
                    "lines": [56],
                },
                {
                    "id": "no-rate-limit",
                    "title": "No rate limiting or lockout on /login",
                    "problem": "Enables brute-force and credential-stuffing attacks.",
                    "fix": "Add rate limiting, track failures, and apply backoff/lockout.",
                    "lines": [28],
                },
                {
                    "id": "plain-http",
                    "title": "Listening on plain HTTP (port 80) by default",
                    "problem": "Tokens and passwords can travel unencrypted if TLS termination isn’t in front.",
                    "fix": "Enforce HTTPS in production and configure HSTS behind TLS.",
                    "lines": [69, 70, 71],
                },
                {
                    "id": "missing-security-headers",
                    "title": "Missing security headers",
                    "problem": "No CSP/HSTS/etc., increasing XSS/clickjacking/MIME-sniffing risk.",
                    "fix": "Add appropriate security headers (often via Spring Security).",
                    "lines": [19],
                },
                {
                    "id": "password-policy-unclear",
                    "title": "Unclear password-handling policy",
                    "problem": "Credentials appear to be compared directly, implying plaintext password handling.",
                    "fix": "Use bcrypt/argon2 hashed passwords and constant-time verification.",
                    "lines": [24, 25, 33],
                },
                {
                    "id": "error-leakage",
                    "title": "Potential verbose error leakage",
                    "problem": "Returning verification exception messages can leak details to clients.",
                    "fix": "Return generic errors; log safely with sanitization and appropriate log levels.",
                    "lines": [52],
                },
            ],
            "cpp": [
                {
                    "id": "hardcoded-secret",
                    "title": "Hard-coded JWT secret",
                    "problem": "A hard-coded secret exposes credentials to anyone with code access.",
                    "fix": "Load from environment/secrets manager and rotate regularly.",
                    "lines": [7],
                },
                {
                    "id": "weak-secret",
                    "title": "Weak / short secret value",
                    "problem": "A simple word is easy to brute-force, breaking HS256 signatures.",
                    "fix": "Use a long random secret (≥ 32 bytes) and rotate regularly.",
                    "lines": [7],
                },
                {
                    "id": "no-exp",
                    "title": "Tokens never expire",
                    "problem": "The token omits an expiration, so stolen tokens work indefinitely.",
                    "fix": "Add exp and enforce it; consider short-lived access tokens + refresh tokens.",
                    "lines": [34, 36],
                },
                {
                    "id": "no-aud-iss",
                    "title": "No audience (aud) or issuer (iss) checks",
                    "problem": "The server will accept tokens minted for other services (confused-deputy risk).",
                    "fix": "Include iss/aud claims and validate them during verification.",
                    "lines": [34, 36, 46, 60],
                },
                {
                    "id": "auth-header-missing-check",
                    "title": "Missing presence check for Authorization header",
                    "problem": "Decoding and verification can run on missing/malformed headers, causing avoidable errors and DoS vectors.",
                    "fix": "Validate the Authorization header format before decoding or verifying.",
                    "lines": [13, 16, 42, 45, 55, 59],
                },
                {
                    "id": "admin-no-role-check",
                    "title": "Privilege escalation on /admin route",
                    "problem": "Any user with a valid token can hit /admin; there’s no role/claim check.",
                    "fix": "Add a role claim and enforce it; otherwise return 403.",
                    "lines": [55],
                },
                {
                    "id": "no-rate-limit",
                    "title": "No rate limiting or lockout on /login",
                    "problem": "Enables brute-force and credential-stuffing attacks.",
                    "fix": "Add rate limiting, track failures, and apply backoff/lockout.",
                    "lines": [23],
                },
                {
                    "id": "plain-http",
                    "title": "Listening on plain HTTP (port 80) by default",
                    "problem": "Tokens and passwords can travel unencrypted if TLS termination isn’t in front.",
                    "fix": "Enforce HTTPS in production and configure HSTS behind TLS.",
                    "lines": [69],
                },
                {
                    "id": "missing-security-headers",
                    "title": "Missing security headers",
                    "problem": "No CSP/HSTS/etc., increasing XSS/clickjacking/MIME-sniffing risk.",
                    "fix": "Set appropriate headers at the edge/proxy or via middleware/framework support.",
                    "lines": [21],
                },
                {
                    "id": "password-policy-unclear",
                    "title": "Unclear password-handling policy",
                    "problem": "Credentials appear to be compared directly, implying plaintext password handling.",
                    "fix": "Use bcrypt/argon2 hashed passwords and constant-time verification.",
                    "lines": [9, 10, 28],
                },
                {
                    "id": "error-leakage",
                    "title": "Potential verbose error leakage",
                    "problem": "Returning raw exception messages can leak sensitive details to clients.",
                    "fix": "Return generic errors; log safely with sanitization and appropriate log levels.",
                    "lines": [51],
                },
            ],
        },
    },
    3: {
        "id": 3,
        "languages": {
            "typescript": [
                {
                    "id": "untrusted-next-redirect",
                    "title": "Untrusted redirect target (open redirect / XSS)",
                    "problem": "The app redirects to a user-controlled `next` value, enabling open redirect and potential XSS via `javascript:`/`data:` URLs.",
                    "fix": "Allowlist relative paths only, reject dangerous schemes/hosts, and validate server-side on POST before redirecting.",
                    "lines": [16, 34],
                },
                {
                    "id": "hidden-input-trust",
                    "title": "Trusting hidden input for security",
                    "problem": "Escaping `next` in the rendered form doesn't secure the POST; an attacker can submit any `next` directly to `/session`.",
                    "fix": "Re-validate and normalize `next` in `/session` and fall back to `/` when invalid.",
                    "lines": [33, 34, 35],
                },
                {
                    "id": "custom-escaping",
                    "title": "Homegrown escaping is fragile",
                    "problem": "Custom escaping is easy to get wrong and is context-dependent (HTML attribute vs URL vs JS).",
                    "fix": "Use a template engine/framework helpers for HTML escaping and keep redirect handling separate with strict URL validation.",
                    "lines": [6, 7, 8, 9, 10, 11, 12, 13, 25],
                },
            ],
            "python": [
                {
                    "id": "untrusted-next-redirect",
                    "title": "Untrusted redirect target (open redirect / XSS)",
                    "problem": "The app redirects to a user-controlled `next` value, enabling open redirect and potential XSS via `javascript:`/`data:` URLs.",
                    "fix": "Allowlist relative paths only, reject dangerous schemes/hosts, and validate server-side on POST before redirecting.",
                    "lines": [18, 37],
                },
                {
                    "id": "hidden-input-trust",
                    "title": "Trusting hidden input for security",
                    "problem": "Escaping `next` in the rendered form doesn't secure the POST; an attacker can submit any `next` directly to `/session`.",
                    "fix": "Re-validate and normalize `next` in `/session` and fall back to `/` when invalid.",
                    "lines": [35, 36, 37],
                },
                {
                    "id": "custom-escaping",
                    "title": "Homegrown escaping is fragile",
                    "problem": "Custom escaping is easy to get wrong and is context-dependent (HTML attribute vs URL vs JS).",
                    "fix": "Use framework templates/helpers for HTML escaping and keep redirect handling separate with strict URL validation.",
                    "lines": [6, 7, 8, 9, 10, 11, 12, 13, 27],
                },
            ],
            "java": [
                {
                    "id": "untrusted-next-redirect",
                    "title": "Untrusted redirect target (open redirect / XSS)",
                    "problem": "The app redirects to a user-controlled `next` value, enabling open redirect and potential XSS via `javascript:`/`data:` URLs.",
                    "fix": "Allowlist relative paths only, reject dangerous schemes/hosts, and validate server-side on POST before redirecting.",
                    "lines": [25, 45],
                },
                {
                    "id": "hidden-input-trust",
                    "title": "Trusting hidden input for security",
                    "problem": "Escaping `next` in the rendered form doesn't secure the POST; an attacker can submit any `next` directly to `/session`.",
                    "fix": "Re-validate and normalize `next` in `/session` and fall back to `/` when invalid.",
                    "lines": [43, 45, 46],
                },
                {
                    "id": "custom-escaping",
                    "title": "Homegrown escaping is fragile",
                    "problem": "Custom escaping is easy to get wrong and is context-dependent (HTML attribute vs URL vs JS).",
                    "fix": "Use templating with auto-escaping and keep redirect handling separate with strict URL validation.",
                    "lines": [13, 14, 15, 16, 17, 18, 19, 20, 21, 34],
                },
            ],
            "cpp": [
                {
                    "id": "untrusted-next-redirect",
                    "title": "Untrusted redirect target (open redirect / XSS)",
                    "problem": "The app redirects to a user-controlled `next` value, enabling open redirect and potential XSS via `javascript:`/`data:` URLs.",
                    "fix": "Allowlist relative paths only, reject dangerous schemes/hosts, and validate server-side on POST before redirecting.",
                    "lines": [26, 45, 47],
                },
                {
                    "id": "hidden-input-trust",
                    "title": "Trusting hidden input for security",
                    "problem": "Escaping `next` in the rendered form doesn't secure the POST; an attacker can submit any `next` directly to `/session`.",
                    "fix": "Re-validate and normalize `next` in `/session` and fall back to `/` when invalid.",
                    "lines": [44, 45, 46, 47, 48],
                },
                {
                    "id": "custom-escaping",
                    "title": "Homegrown escaping is fragile",
                    "problem": "Custom escaping is easy to get wrong and is context-dependent (HTML attribute vs URL vs JS).",
                    "fix": "Use a template engine/framework helpers for HTML escaping and handle redirects with strict URL validation.",
                    "lines": [4, 6, 12, 16, 35],
                },
            ],
        },
    },
    4: {
        "id": 4,
        "languages": {
            "typescript": [
                {
                    "id": "padding-oracle",
                    "title": "Padding oracle via error differences",
                    "problem": "The server returns a different response for padding-related failures, enabling a padding oracle to decrypt/forge ciphertexts.",
                    "fix": "Use authenticated encryption (AES-GCM/ChaCha20-Poly1305) and return uniform errors for all token failures.",
                    "lines": [29, 31, 32, 34],
                },
                {
                    "id": "no-aead",
                    "title": "CBC without authentication",
                    "problem": "AES-CBC provides confidentiality only; without a MAC/AEAD it is malleable and unsafe for tokens.",
                    "fix": "Use an AEAD mode (AES-GCM/ChaCha20-Poly1305) or encrypt-then-MAC with constant-time verification.",
                    "lines": [17, 18],
                },
                {
                    "id": "hardcoded-key",
                    "title": "Hard-coded encryption key",
                    "problem": "Embedding keys in source code makes rotation hard and increases blast radius on leaks.",
                    "fix": "Load keys from a secrets manager / environment and rotate; use per-environment keys with access controls.",
                    "lines": [7, 8, 9, 10],
                },
            ],
            "python": [
                {
                    "id": "padding-oracle",
                    "title": "Padding oracle via error differences",
                    "problem": "The server returns a different response for padding-related failures, enabling a padding oracle to decrypt/forge ciphertexts.",
                    "fix": "Use authenticated encryption (AES-GCM/ChaCha20-Poly1305) and return uniform errors for all token failures.",
                    "lines": [34, 35, 36, 37],
                },
                {
                    "id": "no-aead",
                    "title": "CBC without authentication",
                    "problem": "AES-CBC provides confidentiality only; without a MAC/AEAD it is malleable and unsafe for tokens.",
                    "fix": "Use an AEAD mode (AES-GCM/ChaCha20-Poly1305) or encrypt-then-MAC with constant-time verification.",
                    "lines": [19, 20, 21],
                },
                {
                    "id": "hardcoded-key",
                    "title": "Hard-coded encryption key",
                    "problem": "Embedding keys in source code makes rotation hard and increases blast radius on leaks.",
                    "fix": "Load keys from a secrets manager / environment and rotate; use per-environment keys with access controls.",
                    "lines": [10, 11, 12],
                },
            ],
            "java": [
                {
                    "id": "padding-oracle",
                    "title": "Padding oracle via error differences",
                    "problem": "The server returns a different response for padding-related failures, enabling a padding oracle to decrypt/forge ciphertexts.",
                    "fix": "Use authenticated encryption (AES-GCM/ChaCha20-Poly1305) and return uniform errors for all token failures.",
                    "lines": [53, 54, 55, 56],
                },
                {
                    "id": "no-aead",
                    "title": "CBC without authentication",
                    "problem": "AES-CBC provides confidentiality only; without a MAC/AEAD it is malleable and unsafe for tokens.",
                    "fix": "Use an AEAD mode (AES-GCM/ChaCha20-Poly1305) or encrypt-then-MAC with constant-time verification.",
                    "lines": [39, 40, 41],
                },
                {
                    "id": "hardcoded-key",
                    "title": "Hard-coded encryption key",
                    "problem": "Embedding keys in source code makes rotation hard and increases blast radius on leaks.",
                    "fix": "Load keys from a secrets manager / environment and rotate; use per-environment keys with access controls.",
                    "lines": [23],
                },
            ],
            "cpp": [
                {
                    "id": "padding-oracle",
                    "title": "Padding oracle via error differences",
                    "problem": "The server returns a different response for padding-related failures, enabling a padding oracle to decrypt/forge ciphertexts.",
                    "fix": "Use authenticated encryption (AES-GCM/ChaCha20-Poly1305) and return uniform errors for all token failures.",
                    "lines": [50, 52, 71, 72, 75, 76],
                },
                {
                    "id": "no-aead",
                    "title": "CBC without authentication",
                    "problem": "AES-CBC provides confidentiality only; without a MAC/AEAD it is malleable and unsafe for tokens.",
                    "fix": "Use an AEAD mode (AES-GCM/ChaCha20-Poly1305) or encrypt-then-MAC with constant-time verification.",
                    "lines": [44, 45],
                },
                {
                    "id": "hardcoded-key",
                    "title": "Hard-coded encryption key",
                    "problem": "Embedding keys in source code makes rotation hard and increases blast radius on leaks.",
                    "fix": "Load keys from a secrets manager / environment and rotate; use per-environment keys with access controls.",
                    "lines": [14],
                },
            ],
        },
    },
}


def get_answers(challenge_id: int) -> dict[str, Any] | None:
    return _ANSWERS.get(challenge_id)

