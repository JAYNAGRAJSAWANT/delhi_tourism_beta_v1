/*

Author: Abhijeet Thorat
Project: DTTDC (CAR BOOKING)

This file contain a script that calls the check car vehicle availability
and return a JSON response to further consumen in the Template.

*/
console.log("Calling from File")

document.addEventListener("DOMContentLoaded", function() {
    const journeyDateInput = document.getElementById("id_journeyDate");
    const availabilityBox = document.getElementById("availabilityMessage");
    const submitBtn = document.querySelector("button[type='submit']");

    if (!journeyDateInput) return;

    const CHECK_URL = journeyDateInput.dataset.url;
    //const VEHICLE_DETAIL_ID = journeyDateInput.dataset.vehicleId;
    const VEHICLE_DETAIL_ID = journeyDateInput.dataset.vehicleId;
    console.log(VEHICLE_DETAIL_ID)

    journeyDateInput.addEventListener("change", function () {
        const date = this.value;

        availabilityBox.innerHTML = "";
        submitBtn.disabled = true;

        if (!date) return;

        fetch(`${CHECK_URL}?vehicle_id=${VEHICLE_DETAIL_ID}&journey_date=${date}`)
        .then(response => {
            if (!response.ok) throw new Error("Network error");
            return response.json();
        })
        .then(data => {
            if (data.available) {
                const availableSeats = parseInt(data.seats);

                availabilityBox.innerHTML = `Available Vehicles : ${availableSeats}`
                availabilityBox.className = "text-success small fw-semibold";

                submitBtn.disabled = false;
            }else{
                availabilityBox.innerHTML = data.message || "Not available"
                availabilityBox.className = "text-danger small fw-semibold"
                submitBtn.disabled = true
            }
        })
        .catch(error => {
            console.error("Availability check failed:",error)

            availabilityBox.innerHTML = `
            <div class="alert alert-danger py-2 mb-0">
                Unable to check availability. Try again.
            </div>
            `;
        });
    });
});