$(function () {

    // --------------------------------------------------
    // Enable Enter button when movie is entered
    // --------------------------------------------------

    const source = document.getElementById("autoComplete");

    const inputHandler = function (e) {

        if (e.target.value.trim() === "") {
            $(".movie-button").prop("disabled", true);
        } else {
            $(".movie-button").prop("disabled", false);
        }
    };

    source.addEventListener("input", inputHandler);


    // --------------------------------------------------
    // Search button
    // --------------------------------------------------

    $(".movie-button").on("click", function () {

        const title = $("#autoComplete").val().trim();

        if (title === "") {

            $(".fail").show();
            $(".results").hide();

            return;
        }

        movie_recs(title);
    });


    // --------------------------------------------------
    // Allow Enter key to submit
    // --------------------------------------------------

    $("#autoComplete").on("keypress", function (event) {

        if (event.which === 13) {

            event.preventDefault();

            const title = $(this).val().trim();

            if (title !== "") {
                movie_recs(title);
            }
        }
    });

});


// --------------------------------------------------
// Get recommendations from Flask
// --------------------------------------------------

function movie_recs(movie_title) {

    $(".movie-button").prop("disabled", true);

    $.ajax({

        type: "POST",

        url: "/local-recommend",

        data: {
            name: movie_title
        },

        success: function (response) {

            // Replace the current page with the
            // recommendation results page.
            document.open();

            document.write(response);

            document.close();
        },

        error: function (xhr) {

            console.error(
                "Recommendation error:",
                xhr.responseText
            );

            $(".movie-button").prop("disabled", false);

            alert(
                "Something went wrong while generating recommendations."
            );
        }

    });
}