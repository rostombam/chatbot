/**
 * Chatbot Local BI - script.js
 *
 * This script handles the frontend interactions for the Chatbot Local BI application,
 * including file uploads, data querying, and report generation.
 */

// Global state variables
let currentDfId = null; // Stores the ID/name of the uploaded dataframe (e.g., filename)
let lastUserQuery = ""; // Stores the last user query for report generation context

// DOM Ready Event Listener
document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners to buttons
    // Using direct onclick attributes in HTML for simplicity, but could be done here:
    // document.getElementById('uploadButton').addEventListener('click', uploadFile);
    // document.getElementById('queryButton').addEventListener('click', submitQuery);
    // document.getElementById('reportButton').addEventListener('click', requestReport);
    console.log("Chatbot Local BI script loaded and DOM fully parsed.");
});

/**
 * Toggles the display of a loader element.
 * @param {string} loaderId - The ID of the loader element.
 * @param {boolean} show - True to show the loader, false to hide.
 */
function toggleLoader(loaderId, show) {
    const loaderElement = document.getElementById(loaderId);
    if (loaderElement) {
        loaderElement.style.display = show ? 'block' : 'none';
    }
}

/**
 * Displays a status message to the user.
 * @param {string} elementId - The ID of the element where the status should be shown.
 * @param {string} message - The message to display.
 * @param {boolean} [isError=false] - True if the message is an error, false otherwise.
 */
function showStatus(elementId, message, isError = false) {
    const statusElement = document.getElementById(elementId);
    if (statusElement) {
        statusElement.textContent = message;
        // Bootstrap alert classes for styling
        statusElement.className = isError ? 'alert alert-danger mt-2' : 'alert alert-success mt-2';
        statusElement.style.display = message ? 'block' : 'none';
    }
}

/**
 * Adds a message to the chat history display.
 * @param {string} message - The message content.
 * @param {'user' | 'bot'} type - The type of message ('user' or 'bot').
 */
function addChatMessage(message, type) {
    const chatHistory = document.getElementById('chatHistory');
    if (!chatHistory) return;

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', type === 'user' ? 'user-message' : 'bot-message');

    // Sanitize message content before adding to innerHTML to prevent XSS
    // A more robust sanitizer might be needed for complex HTML, but textContent is safer for plain text.
    const preElement = document.createElement('pre');
    preElement.textContent = message; // Using textContent is safer
    messageDiv.appendChild(preElement); // Append <pre> to preserve formatting from LLM

    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to the latest message
}


/**
 * Handles the file upload process.
 * Reads the selected file and sends it to the backend '/upload' endpoint.
 */
async function uploadFile() {
    const fileInput = document.getElementById('fileUpload');
    const uploadStatusEl = 'uploadStatus'; // ID of the status element

    if (!fileInput || fileInput.files.length === 0) {
        showStatus(uploadStatusEl, 'Please select a file first.', true);
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    toggleLoader('uploadLoader', true);
    showStatus(uploadStatusEl, ''); // Clear previous status
    // Hide data sections until upload is successful
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('querySection').style.display = 'none';
    document.getElementById('reportSection').style.display = 'none';
    currentDfId = null; // Reset dataframe ID

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const result = await response.json(); // Expects JSON response from Flask

        if (response.ok) {
            currentDfId = result.df_id; // Store the DataFrame identifier
            document.getElementById('fileName').textContent = result.df_id;
            document.getElementById('columnList').textContent = result.columns.join(', ');

            // Safely set HTML content for data preview
            const dataPreviewEl = document.getElementById('dataPreview');
            if (dataPreviewEl) dataPreviewEl.innerHTML = result.head; // Assuming result.head is trusted/sanitized HTML

            // Show relevant sections and clear chat
            document.getElementById('previewSection').style.display = 'block';
            document.getElementById('querySection').style.display = 'block';
            document.getElementById('reportSection').style.display = 'none'; // Keep report section hidden initially

            const chatHistoryEl = document.getElementById('chatHistory');
            if (chatHistoryEl) chatHistoryEl.innerHTML = ''; // Clear previous chat history

            addChatMessage(`File "${result.df_id}" uploaded successfully. Columns: ${result.columns.join(', ')}. You can now ask questions about this data.`, 'bot');
            showStatus(uploadStatusEl, result.message || "File uploaded successfully!", false);
        } else {
            showStatus(uploadStatusEl, `Error: ${result.error || 'Unknown upload error'}`, true);
        }
    } catch (error) {
        console.error("Upload error:", error);
        showStatus(uploadStatusEl, `Network error: ${error.message}`, true);
    } finally {
        toggleLoader('uploadLoader', false);
    }
}

/**
 * Submits the user's query to the backend '/query' endpoint.
 * Displays the bot's response in the chat history.
 */
async function submitQuery() {
    const queryInput = document.getElementById('queryInput');
    const queryErrorEl = 'queryError'; // ID of the query error element

    if (!queryInput) return;
    lastUserQuery = queryInput.value.trim(); // Store the user's query

    if (!lastUserQuery) {
        showStatus(queryErrorEl, 'Please enter a query.', true);
        return;
    }
    if (!currentDfId) {
        showStatus(queryErrorEl, 'No data has been uploaded. Please upload a file first.', true);
        return;
    }

    addChatMessage(lastUserQuery, 'user');
    toggleLoader('queryLoader', true);
    showStatus(queryErrorEl, ''); // Clear previous error

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ df_id: currentDfId, query: lastUserQuery }),
        });
        const result = await response.json(); // Expects JSON response

        if (response.ok) {
            addChatMessage(result.response, 'bot');
            // If the response suggests insights, make the report section visible
            if (result.response && (result.response.toLowerCase().includes("insight") || result.response.toLowerCase().includes("trend"))) {
                 document.getElementById('reportSection').style.display = 'block';
                 const textReportContentEl = document.getElementById('textReportContent');
                 if (textReportContentEl) {
                    // Display query response as initial insight, wrapped in <pre> for formatting
                    const preElement = document.createElement('pre');
                    preElement.textContent = result.response;
                    textReportContentEl.innerHTML = ''; // Clear previous content
                    textReportContentEl.appendChild(preElement);
                 }
                 const htmlReportFrameEl = document.getElementById('htmlReportFrame');
                 if (htmlReportFrameEl) htmlReportFrameEl.srcdoc = "<p>Click 'Generate Detailed Report' to see an HTML formatted report based on your query.</p>";
            }
        } else {
            addChatMessage(`Error: ${result.error || 'Unknown query error'}`, 'bot');
            showStatus(queryErrorEl, `Error: ${result.error || 'Failed to get response'}`, true);
        }
    } catch (error) {
        console.error("Query error:", error);
        addChatMessage(`Network error: ${error.message}`, 'bot');
        showStatus(queryErrorEl, `Network error: ${error.message}`, true);
    } finally {
        toggleLoader('queryLoader', false);
        queryInput.value = ''; // Clear input field after submission
    }
}

/**
 * Requests a detailed report from the backend '/generate_report' endpoint.
 * Displays the generated text and HTML reports.
 */
async function requestReport() {
    const reportStatusEl = 'reportStatus'; // ID of the report status element

    if (!currentDfId) {
        showStatus(reportStatusEl, 'Please upload and query data first. The report needs context.', true);
        return;
    }
    if (!lastUserQuery) {
        showStatus(reportStatusEl, 'Please ask a question first to provide context for the report.', true);
        return;
    }

    toggleLoader('reportLoader', true);
    showStatus(reportStatusEl, ''); // Clear previous status
    document.getElementById('reportSection').style.display = 'block'; // Ensure section is visible

    try {
        const response = await fetch('/generate_report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ df_id: currentDfId, query_context: lastUserQuery })
        });
        const result = await response.json(); // Expects JSON with report data

        if (response.ok) {
            showStatus(reportStatusEl, 'Report generated successfully!', false);

            // Display text report (assuming it's pre-formatted or plain text)
            const textReportContentEl = document.getElementById('textReportContent');
            if (textReportContentEl) {
                 const preElement = document.createElement('pre');
                 preElement.textContent = result.text_report || "No text report available.";
                 textReportContentEl.innerHTML = ''; // Clear previous content
                 textReportContentEl.appendChild(preElement);
            }

            // Display HTML report in iframe using srcdoc for security and simplicity
            const htmlReportFrameEl = document.getElementById('htmlReportFrame');
            if (htmlReportFrameEl) {
                htmlReportFrameEl.srcdoc = result.html_report || "<p>No HTML report available.</p>";
            }

            // Activate the first tab (text report) using jQuery for Bootstrap tabs
            if (typeof $ !== 'undefined') {
                $('#reportTab a[href="#textReportContent"]').tab('show');
            }

        } else {
            showStatus(reportStatusEl, `Error generating report: ${result.error || 'Unknown error'}`, true);
            const textReportContentEl = document.getElementById('textReportContent');
            if (textReportContentEl) textReportContentEl.textContent = `Error: ${result.error || 'Failed to generate report.'}`;
            const htmlReportFrameEl = document.getElementById('htmlReportFrame');
            if (htmlReportFrameEl) htmlReportFrameEl.srcdoc = `<h3>Error generating report:</h3><p>${result.error || 'Unknown error'}</p>`;
        }

    } catch (error) {
        console.error("Report generation error:", error);
        showStatus(reportStatusEl, `Network error during report generation: ${error.message}`, true);
        const textReportContentEl = document.getElementById('textReportContent');
        if (textReportContentEl) textReportContentEl.textContent = `Network Error: ${error.message}`;
        const htmlReportFrameEl = document.getElementById('htmlReportFrame');
        if (htmlReportFrameEl) htmlReportFrameEl.srcdoc = `<h3>Network Error:</h3><p>${error.message}</p>`;
    } finally {
        toggleLoader('reportLoader', false);
    }
}

// Expose functions to global window object if they are called directly from HTML onclick
// This is not strictly necessary if you add event listeners programmatically as shown in DOMContentLoaded.
window.uploadFile = uploadFile;
window.submitQuery = submitQuery;
window.requestReport = requestReport;
