// Predefined services for home care and medical care
const services = {
    homecare: ["Housekeeping", "Cooking", "Daily Check-ins", "Weekly Check-ins"],
    medicalcare: ["Blood Test", "Bathing/Dressing", "Nursing", "Physiotherapy"]
};

// Function to update the services based on the selected type
function updateServices() {
    const type = document.getElementById("type").value;
    const serviceDropdown = document.getElementById("service");
    serviceDropdown.innerHTML = '<option value="">Select Service</option>';

    if (type && services[type]) {
        services[type].forEach(service => {
            const option = document.createElement("option");
            option.value = service;
            option.textContent = service;
            serviceDropdown.appendChild(option);
        });
    }
}

// Function to calculate the fare based on the start and end times
function calculateFare() {
    const startTime = document.getElementById("start-time").value;
    const endTime = document.getElementById("end-time").value;

    if (startTime && endTime) {
        const start = new Date('1970-01-01T' + startTime + 'Z');
        const end = new Date('1970-01-01T' + endTime + 'Z');
        const diff = (end - start) / (1000 * 60 * 60); // Difference in hours

        if (diff > 0) {
            const fare = diff * 200; // Example fare rate of ₹200 per hour
            document.getElementById("fare").textContent = fare.toFixed(2);
            document.getElementById("fare-display").style.display = 'block';
        } else {
            alert("End time must be later than start time.");
        }
    } else {
        alert("Please select both start and end times.");
    }
}

// Function to handle cancel button click
function cancelBooking() {
    window.location.href = "dashboard.html"; // Redirect to the homepage
}
