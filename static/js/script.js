const urlInput = document.getElementById('link-input');
const uploadInput = document.getElementById('video');
const startButton = document.getElementById('start-button');
const spinner = document.getElementById('spinner');
const videoPreview = document.getElementById('video-preview');
const filenameDisplay = document.getElementById('filename-display');
const clipsContainer = document.getElementById('clips');

// When user types in URL input
urlInput.addEventListener('input', () => {
    if (urlInput.value.trim() !== "") {
        // Disable file upload and enable start button
        uploadInput.value = null;
        videoPreview.style.display = "none";
        filenameDisplay.textContent = "";
        startButton.disabled = false;
    } else {
        if (!uploadInput.files.length) {
            startButton.disabled = true;
        }
    }
});

// When user selects a file
function onFileSelected(input) {
    const file = input.files[0];
    if (file) {
        const videoURL = URL.createObjectURL(file);
        videoPreview.src = videoURL;
        videoPreview.style.display = "block";
        filenameDisplay.textContent = file.name;
        urlInput.value = ""; // Clear URL input
        startButton.disabled = false;
    }
}

// Main function to start clipping process
function startClipping() {
    // Disable button to prevent multiple clicks
    startButton.disabled = true;

    // Show spinner
    spinner.style.display = "block";

    // Clear previous clips
    clipsContainer.innerHTML = "";

    let fetchPromise;

    if (urlInput.value.trim() !== "") {
        // Handle URL input
        const url = urlInput.value.trim();
        fetchPromise = fetch('/download_link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
    } else if (uploadInput.files.length > 0) {
        // Handle file upload
        const formData = new FormData();
        formData.append('video', uploadInput.files[0]);
        fetchPromise = fetch('/upload', {
            method: 'POST',
            body: formData
        });
    } else {
        alert("Please upload a video or enter a live stream URL.");
        spinner.style.display = "none";
        startButton.disabled = false;
        return;
    }

    // Process response
    fetchPromise
        .then(response => {
            if (!response.ok) throw new Error("Server error: " + response.statusText);
            return response.json();
        })
        .then(data => {
            showClips(data);
        })
        .catch(err => {
            alert("Error: " + err.message);
        })
        .finally(() => {
            // Hide spinner and re-enable button
            spinner.style.display = "none";
            startButton.disabled = false;
        });
}

// Show clips in UI
function showClips(data) {
    clipsContainer.innerHTML = "";  // Clear previous results

    if (data.clips && data.clips.length > 0) {
        clipsContainer.innerHTML += data.clips.map(clip => 
            `<video src="${clip}" controls style="width: 100%; max-width: 400px; margin-bottom: 10px;"></video>`
        ).join('');
    } else {
        clipsContainer.innerHTML += "<p>No clips found.</p>";
    }

    if (data.topics && data.topics.length > 0) {
        const topicsHtml = data.topics.map(topic => 
            `<p><strong>${topic[0]}</strong>: ${topic[1]}</p>`
        ).join('');
        clipsContainer.innerHTML += `<h3>Detected Topics:</h3>` + topicsHtml;
    }
}