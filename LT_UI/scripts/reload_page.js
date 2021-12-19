let lastUpdate;

fetch('/tasks/api/get_update/')
  .then(response => response.json())
  .then(timeString => lastUpdate = timeString);

setInterval(checkForUpdate, 60 * 1000);

function checkForUpdate() {
  fetch('/tasks/api/get_update/')
    .then(response => response.json())
    .then(timeString => {
      if (lastUpdate !== timeString) {
        location.reload()
      }
    });
}