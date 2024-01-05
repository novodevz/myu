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

// You can add more general functions here, if needed.
