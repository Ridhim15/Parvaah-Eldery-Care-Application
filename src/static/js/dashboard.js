console.log("Dashboard script loaded")

let holdTimeout
let holdTime = 3000 // 3 seconds
let interval

function startHold(event, buttonType) {
	let startTime = Date.now()
	const button = event.currentTarget
	const timerSpan = document.getElementById(buttonType + "-timer")

	let remainingTime = holdTime / 1000
	timerSpan.innerText = `${remainingTime}s`

	interval = setInterval(() => {
		remainingTime -= 1
		timerSpan.innerText = `${remainingTime}s`
	}, 1000)

	holdTimeout = setTimeout(() => {
		clearInterval(interval)
		timerSpan.innerText = buttonType === "emergency" ? "Emergency" : "SOS"

		if (buttonType === "emergency") {
			window.location.href = "/emergency"
		} else if (buttonType === "sos") {
			window.location.href = "/sos"
		}
	}, holdTime)
}

function endHold(event) {
	const button = event.currentTarget
	const buttonType = button.classList.contains("emergency-btn") ? "emergency" : "sos"
	const timerSpan = document.getElementById(buttonType + "-timer")

	clearTimeout(holdTimeout)
	clearInterval(interval)

	timerSpan.innerText = buttonType === "emergency" ? "Emergency" : "SOS"
}
function refreshUpcomingSection() {
	fetch("/refresh-upcoming")
		.then(response => {
			if (!response.ok) {
				throw new Error("Network response was not ok")
			}
			return response.text()
		})
		.then(html => {
			document.querySelector(".upcoming-section").innerHTML = html
		})
		.catch(error => console.error("Error refreshing appointments and reminders:", error))
}

// Refresh every 10 seconds
setInterval(refreshUpcomingSection, 10000)

