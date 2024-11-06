console.log("Login script loaded")
const inputs = document.querySelectorAll(".input-field")
const toggle_btn = document.querySelectorAll(".toggle")
const main = document.querySelector("main")
const bullets = document.querySelectorAll(".bullets span")
const images = document.querySelectorAll(".image")
const texts = document.querySelectorAll(".text") // Add this line to select text elements

console.log("Login works")
inputs.forEach(inp => {
	inp.addEventListener("focus", () => {
		inp.classList.add("active")
	})
	inp.addEventListener("blur", () => {
		if (inp.value != "") return
		inp.classList.remove("active")
	})
})

toggle_btn.forEach(btn => {
	btn.addEventListener("click", () => {
		main.classList.toggle("sign-up-mode")
	})
})

function moveSlider() {
	let index = this.dataset.value

	let currentImage = document.querySelector(`.img-${index}`)
	images.forEach(img => img.classList.remove("show"))
	currentImage.classList.add("show")

	let currentText = document.querySelector(`.text-${index}`)
	texts.forEach(text => text.classList.remove("show")) // Loop through text elements
	currentText.classList.add("show")

	bullets.forEach(bull => bull.classList.remove("active"))
	this.classList.add("active")
}

bullets.forEach(bullet => {
	bullet.addEventListener("click", moveSlider)
})

let currentIndex = 1
setInterval(() => {
	moveSlider.call(bullets[currentIndex - 1]) // Use call to set the correct context
	currentIndex = (currentIndex % bullets.length) + 1 // Cycle through bullets
}, 5000)

