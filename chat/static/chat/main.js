function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const statusMsg = document.getElementById('status-message');

if (fileInput) {
    fileInput.addEventListener('change', () => {
        fileList.innerHTML = '';
        for (let file of fileInput.files) {
            const div = document.createElement('div');
            div.textContent = `- ${file.name}`;
            fileList.appendChild(div);
        }
    });
}

function showStatus(msg, isError = false) {
    statusMsg.textContent = msg;
    statusMsg.className = isError ? "text-xs text-red-600 bg-red-50 p-2 rounded mt-2" : "text-xs text-green-600 bg-green-50 p-2 rounded mt-2";
    statusMsg.classList.remove('hidden');
    setTimeout(() => statusMsg.classList.add('hidden'), 5000);
}

async function uploadContext() {
    const formData = new FormData();
    const files = fileInput.files;
    for (let i = 0; i < files.length; i++) {
        formData.append('documents', files[i]);
    }
    formData.append('text_context', document.getElementById('text-context').value);

    showStatus("Processing and embedding context... This may take a moment on first run.");

    try {
        const response = await fetch('/api/upload_context/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
            showStatus(`Successfully added ${data.chunks_added} chunks to knowledge base!`);
            fileInput.value = '';
            fileList.innerHTML = '';
            document.getElementById('text-context').value = '';
        } else {
            showStatus(`Error: ${data.error}`, true);
        }
    } catch (error) {
        showStatus("Failed to upload context.", true);
    }
}

async function clearContext() {
    try {
        const response = await fetch('/api/clear_context/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken }
        });
        const data = await response.json();
        showStatus("Knowledge base cleared.");
    } catch (error) {
        showStatus("Failed to clear context.", true);
    }
}

const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

function addMessage(role, text, context = null) {
    const wrapper = document.createElement('div');
    wrapper.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const bubble = document.createElement('div');
    bubble.className = `max-w-[80%] p-4 rounded-lg shadow ${role === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 border border-gray-200'}`;
    
    let html = `<div class="whitespace-pre-wrap">${text}</div>`;
    if (context && context.length > 0) {
        html += `<details class="mt-3 text-xs text-gray-500 border-t pt-2">
            <summary class="cursor-pointer font-semibold">View Retrieved Context (${context.length} chunks)</summary>
            <div class="mt-2 space-y-2">
                ${context.map(c => `<div class="bg-gray-50 p-2 rounded border text-gray-600">${c}</div>`).join('')}
            </div>
        </details>`;
    }
    
    bubble.innerHTML = html;
    wrapper.appendChild(bubble);
    chatWindow.appendChild(wrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendQuery() {
    const query = chatInput.value.trim();
    if (!query) return;

    addMessage('user', query);
    chatInput.value = '';
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Thinking...';

    const loadingWrapper = document.createElement('div');
    loadingWrapper.className = 'flex justify-start';
    loadingWrapper.id = 'loading-indicator';
    loadingWrapper.innerHTML = `<div class="bg-white text-gray-500 p-4 rounded-lg border border-gray-200 flex items-center gap-2">
        <i class="fas fa-circle-notch fa-spin"></i> Analyzing documents...
    </div>`;
    chatWindow.appendChild(loadingWrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch('/api/query_rag/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken 
            },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        
        const indicator = document.getElementById('loading-indicator');
        if (indicator) indicator.remove();
        
        if (data.error) {
            addMessage('ai', `Error: ${data.error}`);
        } else {
            addMessage('ai', data.response, data.context_used);
        }
    } catch (error) {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) indicator.remove();
        addMessage('ai', 'Failed to get response from the server.');
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
    }
}