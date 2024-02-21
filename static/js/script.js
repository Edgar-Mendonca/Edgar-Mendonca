// Get the rocket element
var rocket = document.getElementById("rocket");

// Initially hide the rocket
rocket.style.display = "none";

// When the user scrolls down 25px from the top of the document, show the rocket
window.onscroll = function() {
    scrollFunction();
};

function scrollFunction() {
    if (window.scrollY > 25) {
        rocket.style.display = "block";
    } else {
        rocket.style.display = "none";
    }
}

// When the user clicks on the rocket, scroll to the top of the document and animate the rocket
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}
