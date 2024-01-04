// Function to load page content dynamically
async function loadPage(page) {
    try {
        // Fetch the page content from the server
        const response = await axios.get(`http://localhost:5500/frontend/${page}.html`);

        // Update the content div with the fetched HTML
        document.getElementById('content').innerHTML = response.data;

        // Dispatch an event when loadPage completes
        const event = new Event("loadPageComplete");
        window.dispatchEvent(event);
    } catch (error) {
        console.error('Error fetching page content:', error);
    }
}


// Function to fetch the welcome message
function fetchWelcomeMessage() {
    axios.get('http://localhost:5000/')  // Adjust the URL if needed
        .then(response => {
            // Update the welcome message in the HTML
            document.getElementById('welcome-message').textContent = response.data.message;
        })
        .catch(error => {
            console.error('Error fetching welcome message:', error);
        });
}

// You can add more general functions here, if needed.
