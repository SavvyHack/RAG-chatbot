function getQuery() {
    return document.getElementById('query').value.trim();
}

function setResponse(html) {
    document.getElementById('response').innerHTML = html;
}

function submit() {
    const query = getQuery();
    if (!query) {
        setResponse('Please enter a query.');
        return;
    }

    fetch(`/api/dialogpt/?query=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                setResponse(`Error: ${data.error}`);
            } else {
                setResponse(`<strong>DialoGPT:</strong> ${data.response}`);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            setResponse('Error occurred while sending the request.');
        });
}

function askgemini() {
    const query = getQuery();
    if (!query) {
        setResponse('Please enter a query.');
        return;
    }

    // Note: this calls our own backend, which holds the Gemini API key
    // server-side. The key is never sent to, or visible from, the browser.
    fetch(`/api/gemini/?query=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                setResponse(`<strong>Gemini:</strong> Error: ${data.error}`);
            } else {
                setResponse(`<strong>Gemini:</strong> ${data.response}`);
            }
        })
        .catch((error) => {
            console.error('Error calling Gemini API:', error);
            setResponse('<strong>Gemini:</strong> Error calling the Gemini API');
        });
}
