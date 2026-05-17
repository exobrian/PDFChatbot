// Automatically pull history threads immediately following template layout mapping rendering
window.onload = async () => {
    const chatWindow = document.getElementById('chat-window');
    try {
        const res = await fetch('/history');
        const history = await res.json();
        history.forEach(item => {
            chatWindow.innerHTML += `<div class="message user"><b>You:</b> ${item.query}</div>`;
            chatWindow.innerHTML += `<div class="message ai"><b>AI:</b> ${item.answer}</div>`;
        });
        chatWindow.scrollTop = chatWindow.scrollHeight;
    } catch (e) {
        console.error("Historical chat index array initialization fault.", e);
    }
};

async function uploadPDF(files) {
    const status = document.getElementById('file-status');
    const file = files[0];

    if (!file) return;
    status.innerText = "Analyzing text data extraction...";

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        
        if (res.ok) {
            status.innerText = data.filename + " (Ingested)";
        } else {
            status.innerText = "Error: " + data.error;
        }
    } catch (err) {
        status.innerText = "Upload failed.";
    }
}

async function sendChatMessage() {
    const input = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const query = input.value.trim();

    if (!query) return;

    chatWindow.innerHTML += `<div class="message user"><b>You:</b> ${query}</div>`;
    input.value = "";

    const aiBubble = document.createElement('div');
    aiBubble.className = "message ai";
    aiBubble.innerHTML = "<b>AI:</b> Thinking...";
    chatWindow.appendChild(aiBubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: query })
    });
    
    const data = await res.json();
    aiBubble.innerHTML = `<b>AI:</b> ${data.answer}`;
    chatWindow.scrollTop = chatWindow.scrollHeight;
}