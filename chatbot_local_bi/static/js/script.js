document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const uploadButton = document.getElementById('upload-button');
    const fileInput = document.getElementById('file-input');
    const fileNameSpan = document.getElementById('file-name');
    const statusSpan = document.getElementById('status');
    let currentFileId = null;

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('bubble');
        bubbleDiv.innerHTML = text; // Utilisez innerHTML pour rendre le HTML des graphiques

        messageDiv.appendChild(bubbleDiv);
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        messageInput.value = '';
        statusSpan.textContent = 'En train de réfléchir...';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, file_id: currentFileId })
            });
            const data = await response.json();
            addMessage(data.response, 'bot');
        } catch (error) {
            addMessage("Désolé, une erreur de communication est survenue.", 'bot');
            console.error('Error:', error);
        } finally {
            statusSpan.textContent = 'Prêt';
        }
    }

    uploadButton.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        fileNameSpan.textContent = `Téléversement de ${file.name}...`;
        statusSpan.textContent = 'Téléversement...';
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                currentFileId = data.file_id;
                fileNameSpan.textContent = file.name;
                addMessage(`Fichier "${file.name}" téléversé avec succès. Vous pouvez maintenant poser des questions à son sujet.`, 'bot');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            fileNameSpan.textContent = 'Échec du téléversement.';
            addMessage(`Erreur lors du téléversement : ${error.message}`, 'bot');
            console.error('Upload Error:', error);
        } finally {
            statusSpan.textContent = 'Prêt';
            fileInput.value = ''; // Reset file input
        }
    });

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    addMessage("Bonjour ! Téléversez un fichier (PDF, JPG, DOCX, XLSX) et posez-moi une question.", 'bot');
});
