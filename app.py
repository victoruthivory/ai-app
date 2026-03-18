from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

API_KEY = "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"

usage_count = 0
MAX_FREE = 5


@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <title>My AI Assistant</title>
        <style>
            body {
                font-family: Arial;
                background: #343541;
                color: white;
                display: flex;
                flex-direction: column;
                height: 100vh;
                margin: 0;
            }
            #chat {
                flex: 1;
                padding: 10px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            .msg {
                margin: 10px;
                padding: 10px;
                border-radius: 8px;
                max-width: 80%;
            }
            .user {
                background: #0084ff;
                align-self: flex-end;
            }
            .ai {
                background: #444654;
                align-self: flex-start;
            }
            #inputArea {
                display: flex;
                padding: 10px;
                background: #202123;
                position: sticky;
                bottom: 0;
            }
            input {
                flex: 1;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            button {
                margin-left: 10px;
                padding: 10px;
                background: #19c37d;
                border: none;
                border-radius: 5px;
                color: white;
            }
            select {
                margin: 10px;
                padding: 5px;
            }
        </style>
    </head>
    <body>

        <select id="mode">
            <option value="general">General</option>
            <option value="student">Student</option>
            <option value="business">Business</option>
        </select>

        <div id="chat"></div>

        <div id="inputArea">
            <input id="msg" placeholder="Type your message..." />
            <button onclick="send()">Send</button>
        </div>

        <script>
            async function send() {
                let message = document.getElementById("msg").value;
                let mode = document.getElementById("mode").value;

                if (!message) return;

                let chat = document.getElementById("chat");

                let userMsg = document.createElement("div");
                userMsg.className = "msg user";
                userMsg.innerText = message;
                chat.appendChild(userMsg);

                document.getElementById("msg").value = "";

                let typing = document.createElement("div");
                typing.className = "msg ai";
                typing.innerText = "AI is typing...";
                chat.appendChild(typing);

                let res = await fetch("/ask", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        message: message,
                        mode: mode
                    })
                });

                let data = await res.json();

                typing.remove();

                let aiMsg = document.createElement("div");
                aiMsg.className = "msg ai";
                aiMsg.innerText = data.reply || "Error";
                chat.appendChild(aiMsg);

                chat.scrollTop = chat.scrollHeight;
            }

            document.getElementById("msg").addEventListener("keypress", function(e) {
                if (e.key === "Enter") {
                    send();
                }
            });
        </script>

    </body>
    </html>
    """)


@app.route("/ask", methods=["POST"])
def ask():
    try:
        global usage_count

        if usage_count >= MAX_FREE:
            return jsonify({
                "reply": "Free limit reached. Upgrade to premium 💰"
            })

        user_input = request.json.get("message")
        mode = request.json.get("mode", "general")

        messages = []

        if mode == "student":
            messages.append({
                "role": "system",
                "content": "You are a helpful tutor. Explain clearly and simply."
            })
        elif mode == "business":
            messages.append({
                "role": "system",
                "content": "You are a business expert. Give practical, money-making advice."
            })
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant."
            })

        messages.append({
            "role": "user",
            "content": user_input
        })

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": messages
            }
        )

        data = response.json()

        if "choices" in data:
            answer = data["choices"][0]["message"]["content"]
            usage_count += 1
            return jsonify({"reply": answer})
        else:
            return jsonify({"error": data})

    except Exception as e:
        return jsonify({"error": str(e)})


app.run(host="0.0.0.0", port=5000)
