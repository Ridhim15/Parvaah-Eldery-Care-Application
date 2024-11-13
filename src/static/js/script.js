function toggleNav() {
	const overlayMenu = document.getElementById("overlayMenu")
	overlayMenu.classList.toggle("active")

	// Add an event listener to close the overlay when clicking on empty space
	if (overlayMenu.classList.contains("active")) {
		overlayMenu.addEventListener("click", closeOnOutsideClick)
	} else {
		overlayMenu.removeEventListener("click", closeOnOutsideClick)
	}
}

function closeOnOutsideClick(event) {
	const overlayLinks = document.querySelector(".overlay-links")

	// Check if the click was outside the links container
	if (!overlayLinks.contains(event.target)) {
		toggleNav() // Close the overlay
	}
}
