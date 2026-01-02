from flask import Flask, send_file, render_template_string, request
import random
import re
from io import BytesIO
import pyotp
import base64
import hashlib
from urllib.parse import unquote

app = Flask(__name__)

def random_pastel_color():
    r = random.randint(180, 255)
    g = random.randint(180, 255)
    b = random.randint(180, 255)
    return f"rgb({r},{g},{b})"

def generate_otp_svg(secret, width=300, height=160):
    totp = pyotp.TOTP(secret)
    otp = totp.now()

    bg_color = random_pastel_color()
    otp_font_size = 36
    label_font_size = 20
    svg_content = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{bg_color}" />
        <style>
            .label {{
                font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
                font-size: {label_font_size}px;
                font-weight: bold;
                fill: #333333;
                text-anchor: middle;
            }}
            .otp {{
                font-family: 'Courier New', monospace;
                font-size: {otp_font_size}px;
                font-weight: bold;
                fill: #333333;
                text-anchor: middle;
            }}
        </style>
        <text x="{width/2}" y="45" class="label">OTP</text>
        <text x="{width/2}" y="110" class="otp">{otp}</text>
    </svg>"""
    return svg_content

def generate_error_svg(width=300, height=160):
    bg_color = "#ffebee"
    svg_content = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{bg_color}" />
        <style>
            .error {{
                font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
                font-size: 16px;
                font-weight: bold;
                fill: #d32f2f;
                text-anchor: middle;
            }}
        </style>
        <text x="150" y="50" class="error">Invalid URL format</text>
        <text x="150" y="70" class="error" font-size="14">Use /secret_key</text>
    </svg>"""
    return svg_content

@app.route('/favicon.ico')
def favicon():
    return '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="#4caf50"/>
    <text x="50" y="60" font-family="Arial" font-size="40" text-anchor="middle" fill="white">🔑</text>
</svg>
''', 200, {'Content-Type': 'image/svg+xml'}

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>OTP SVG Generator</title>
    <link rel="icon" href="/favicon.ico" type="image/svg+xml">
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background-color: #f8f9fa;
            color: #333;
        }
        .container {
            text-align: center;
            width: 300px;
        }
        .inputs {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 20px;
        }
        input {
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #4caf50;
        }
        input::placeholder {
            color: #adb5bd;
        }
        .preview-container {
            margin-bottom: 15px;
        }
        iframe {
            border: none;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: white;
            width: 300px;
            height: 160px;
        }
        button {
            padding: 10px 16px;
            background-color: #4caf50;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
            width: 100%;
            margin-bottom: 10px;
        }
        button:hover {
            background-color: #388e3c;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        #copyBtn {
            background-color: #2196f3;
        }
        #copyBtn:hover {
            background-color: #0b7dda;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="inputs">
            <input type="text" id="secret" placeholder="Secret Key" autofocus>
        </div>
        <div class="preview-container">
            <iframe id="preview" width="300" height="160" frameborder="0"></iframe>
        </div>
        <button id="copyBtn" disabled>Copy URL</button>
    </div>
    <script>
        const secretInput = document.getElementById('secret');
        const preview = document.getElementById('preview');
        const copyBtn = document.getElementById('copyBtn');

        let debounceTimer;
        function updatePreview() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const secret = secretInput.value;
                if (secret) {
                    const url = `/${encodeURIComponent(secret)}`;
                    preview.src = url;
                    copyBtn.disabled = false;

                    copyBtn.onclick = () => {
                        const fullUrl = `${window.location.origin}${url}`;
                        navigator.clipboard.writeText(fullUrl)
                            .then(() => {
                                copyBtn.textContent = 'Copied!';
                                setTimeout(() => {
                                    copyBtn.textContent = 'Copy URL';
                                }, 2000);
                            });
                    };
                } else {
                    copyBtn.disabled = true;
                }
            }, 300);
        }

        secretInput.addEventListener('input', updatePreview);
    </script>
</body>
</html>
''')

@app.route('/<path:secret>')
def otp(secret):
    secret = unquote(secret)
    if secret:
        svg = generate_otp_svg(secret)
    else:
        svg = generate_error_svg()
    svg_io = BytesIO(svg.encode('utf-8'))
    return send_file(svg_io, mimetype='image/svg+xml', as_attachment=False)

if __name__ == '__main__':
    app.run(port=5003, debug=True)
