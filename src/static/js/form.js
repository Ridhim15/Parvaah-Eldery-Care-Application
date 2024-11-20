// Initialize the form validation

function previewImage(event) {
	const reader = new FileReader()
	reader.onload = function () {
		const output = document.getElementById("profilePic")
		output.src = reader.result
	}
	reader.readAsDataURL(event.target.files[0])
}

// Calculatiing age from date of birth

document.getElementById("dob").addEventListener("change", function () {
	const dob = new Date(this.value)
	const age_section = document.getElementById("age_section")
	const ageSpan = document.getElementById("age")
	const today = new Date()
	let age = today.getFullYear() - dob.getFullYear()
	const monthDiff = today.getMonth() - dob.getMonth()
	if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
		age--
	}
	age_section.style.display = "block"
	ageSpan.textContent = age + " Years old"
})

// Adding selected diseases to the list

document.getElementById("diseases").addEventListener("change", function () {
	const selectedOption = this.options[this.selectedIndex]
	if (selectedOption.value === "none") return

	const li = document.createElement("li")
	li.textContent = selectedOption.text
	li.dataset.value = selectedOption.value

	document.getElementById("selectedDiseases").appendChild(li)
	this.remove(this.selectedIndex)

	li.addEventListener("click", function () {
		const option = new Option(li.textContent, li.dataset.value)
		document.getElementById("diseases").add(option)
		li.remove()
	})

	// Create hidden input field for the selected disease
	const input = document.createElement("input")
	input.type = "hidden"
	input.name = "diseases[]"
	input.value = selectedOption.value
	li.appendChild(input)
})

// Ensure hidden inputs are included in the form submission
document.getElementById("form").addEventListener("submit", function () {
	const selectedDiseases = document.getElementById("selectedDiseases").children
	for (let i = 0; i < selectedDiseases.length; i++) {
		const input = selectedDiseases[i].querySelector("input")
		if (input) {
			this.appendChild(input)
		}
	}
})

// Fetching suggestions for guardian details
function fetchSuggestions() {
	const email = document.getElementById("guardian_email").value
	if (email.length > 0) {
		fetch("/suggest", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: new URLSearchParams({ query: email }),
		})
			.then(response => response.json())
			.then(data => {
				const suggestionsDiv = document.getElementById("suggestions")
				suggestionsDiv.innerHTML = ""
				data.forEach(item => {
					const suggestion = document.createElement("div")
					suggestion.classList.add("suggestion-box")
					suggestion.innerText = item.email
					suggestion.onclick = () => toggleGuardianDetails(item, suggestion)
					suggestionsDiv.appendChild(suggestion)
				})
			})
	}
}

function toggleGuardianDetails(data, element) {
	const isSelected = element.classList.contains("selected")
	const suggestions = document.querySelectorAll(".suggestion-box")

	// Unselect all suggestions
	suggestions.forEach(suggestion => {
		suggestion.classList.remove("selected")
		suggestion.style.backgroundColor = "transparent"
	})

	if (!isSelected) {
		// Select the clicked suggestion
		element.classList.add("selected")
		element.style.backgroundColor = "lightgreen"
		document.getElementById("guardian_email").value = data.email
		document.getElementById("guardian_address").value = data.address
		document.getElementById("guardian_phone").value = data.phone
		document.getElementById("guardian_address").readOnly = true
		document.getElementById("guardian_phone").readOnly = true
	} else {
		// Unselect the clicked suggestion
		document.getElementById("guardian_email").value = ""
		document.getElementById("guardian_address").value = ""
		document.getElementById("guardian_phone").value = ""
		document.getElementById("guardian_address").readOnly = false
		document.getElementById("guardian_phone").readOnly = false
	}
}


// Initialize the phone input field
const phoneInputField = document.querySelector("#phone")
const phoneInput = window.intlTelInput(phoneInputField, {
	utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
})


