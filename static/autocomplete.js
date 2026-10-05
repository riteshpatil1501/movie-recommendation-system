document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("autoComplete");

    if (!input) {
        console.error("Autocomplete input not found.");
        return;
    }

    const movieList = Array.isArray(window.films) ? window.films : [];

    console.log("Autocomplete loaded with", movieList.length, "movies.");

    // Create dropdown
    const dropdown = document.createElement("div");
    dropdown.id = "movieSuggestions";

    input.parentElement.appendChild(dropdown);

    // Hide initially
    dropdown.style.display = "none";

    // Search movies
    input.addEventListener("input", function () {

        const query = input.value.trim().toLowerCase();

        dropdown.innerHTML = "";

        if (query.length < 1) {
            dropdown.style.display = "none";
            return;
        }

        // Find matching movies
        const matches = movieList
            .filter(movie =>
                String(movie).toLowerCase().includes(query)
            )
            .slice(0, 8);

        if (matches.length === 0) {
            dropdown.style.display = "none";
            return;
        }

        // Create suggestions
        matches.forEach(function (movie) {

            const item = document.createElement("div");

            item.className = "movie-suggestion";
            item.textContent = movie;

            item.addEventListener("mousedown", function (event) {

                event.preventDefault();

                input.value = movie;

                dropdown.innerHTML = "";
                dropdown.style.display = "none";

                const button = document.querySelector(".movie-button");

                if (button) {
                    button.disabled = false;
                }
            });

            dropdown.appendChild(item);
        });

        dropdown.style.display = "block";
    });

    // Hide dropdown when clicking elsewhere
    document.addEventListener("click", function (event) {

        if (
            event.target !== input &&
            !dropdown.contains(event.target)
        ) {
            dropdown.style.display = "none";
        }

    });

});