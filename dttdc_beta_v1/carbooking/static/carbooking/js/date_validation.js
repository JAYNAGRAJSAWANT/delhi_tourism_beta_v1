/*

AUTHOR: JAY SAWANT
PROJECT: DTTDC (CAR BOOKING)

THIS IS A SIMPLE DATE VALIDTION JS FUNCTION.
IT BLOCK PAST DATES IN THE DATE INPUT CALENDER.

*/

document.addEventListener("DOMContentLoaded", function () {
  const dateInput = document.getElementById("id_journeyDate");
  if (!dateInput) return;

  const minDate = new Date();
  minDate.setDate(minDate.getDate() + 2);

  const yyyy = minDate.getFullYear();
  const mm = String(minDate.getMonth() + 1).padStart(2, "0");
  const dd = String(minDate.getDate()).padStart(2, "0");

  dateInput.min = `${yyyy}-${mm}-${dd}`;
});