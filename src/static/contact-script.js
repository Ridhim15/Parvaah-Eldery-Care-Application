console.log("Contact script loaded")

const teamMembers = [
	{ name: "YASH", id: "08614902022", image: "https://via.placeholder.com/128" },
	{ name: "ADITYA JAIN", id: "36014902022", image: "https://via.placeholder.com/128" },
	{ name: "RIDHIM GUPTA", id: "07314902022", image: "https://via.placeholder.com/128" },
	{ name: "ADNAAN NANDA", id: "36114902022", image: "https://via.placeholder.com/128" },
]

function createTeamMemberCard(member) {
	const card = document.createElement("div")
	card.className = "team-member"

	const img = document.createElement("img")
	img.src = member.image
	img.alt = member.name

	const name = document.createElement("h2")
	name.textContent = member.name

	const id = document.createElement("p")
	id.textContent = member.id

	card.appendChild(img)
	card.appendChild(name)
	card.appendChild(id)

	return card
}

function populateTeamGrid() {
	const teamGrid = document.getElementById("teamGrid")
	teamMembers.forEach(member => {
		const card = createTeamMemberCard(member)
		teamGrid.appendChild(card)
	})
}

document.addEventListener("DOMContentLoaded", populateTeamGrid)

