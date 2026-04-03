
/* ---------------- CHAT FUNCTION ---------------- */

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (!message) return;

    const chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `<p><b>You:</b> ${message}</p>`;
    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        const aiReply = data.reply ? data.reply : "Something went wrong.";

        chatBox.innerHTML += `<p><b>AI:</b> ${aiReply}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;


    } catch (error) {
        chatBox.innerHTML += `<p><b>AI:</b> Server error. Please try again.</p>`;
    }
}

/* ---------------- TEXT TO SPEECH ---------------- */


function goToResponse() {
    const message = document.getElementById("user-input").value.trim();
    if (!message) return;

    localStorage.setItem("userMessage", message);
    window.location.href = "/response";
}
window.onload = async function () {
    const responseBox = document.getElementById("response-box");
    if (!responseBox) return;

    const message = localStorage.getItem("userMessage");
    if (!message) return;

    responseBox.innerHTML = `<p><b>You:</b> ${message}</p>`;

    const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const data = await res.json();
    responseBox.innerHTML += `<p><b>AI:</b> ${data.reply}</p>`;

};
function goBack() {
    localStorage.removeItem("userMessage");
    window.location.href = "/";
}
recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    localStorage.setItem("userMessage", transcript);
    window.location.href = "/response";
};

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");

    if (!input) return;

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault(); // stop newline
            goToResponse(); // or sendMessage() depending on your flow
        }
    });
});
