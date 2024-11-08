console.log("Bookings script loaded")

document.addEventListener("DOMContentLoaded", event => {
	const urlParams = new URLSearchParams(window.location.search)
	const type = urlParams.get("type")
	const service = urlParams.get("service")

	if (type) {
		document.getElementById("type").value = type
		updateServices(service) // Pass the service to pre-select it
	}
})

const services = {
	homecare: ["Housekeeping", "Cooking", "Laundary"],
	medicalcare: ["Blood Test", "Bathing/Dressing", "Nursing", "Physiotherapy"],
}

function updateServices(selectedService = "") {
	const type = document.getElementById("type").value
	const serviceDropdown = document.getElementById("service")
	serviceDropdown.innerHTML = '<option value="">Select Service</option>'

	if (type && services[type]) {
		services[type].forEach(service => {
			const option = document.createElement("option")
			option.value = service
			option.textContent = service
			serviceDropdown.appendChild(option)
		})

		// Select the service if passed
		if (selectedService) {
			serviceDropdown.value = selectedService
		}
	}
}

function calculateFare() {
	const startDate = document.getElementById("start-date").value
	const startTime = document.getElementById("start-time").value
	const endDate = document.getElementById("end-date").value
	const endTime = document.getElementById("end-time").value

	if (startDate && startTime && endDate && endTime) {
		const start = new Date(startDate + "T" + startTime + "Z")
		const end = new Date(endDate + "T" + endTime + "Z")
		const diff = (end - start) / (1000 * 60 * 60)
		console.log("Start date n time:", start, "End date n time", end, "Diff", diff)
		if (diff > 0) {
			const fare = diff * 200
			document.getElementById("fare").textContent = fare.toFixed(2)
			document.getElementById("fare-display").style.display = "block"
		} else {
			alert("End date and time must be later than start date and time.")
		}
	} else {
		alert("Please select both start and end dates and times.")
	}
}

function cancelBooking() {
	window.history.back()
}
