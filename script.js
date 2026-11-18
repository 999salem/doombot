(() => {
  // The screening time is interpreted in the theatre's Pacific time zone.
  const target = new Date("2026-12-18T05:00:00Z"); // Dec 17, 2026 at 9:00 PM America/Vancouver (PST)
  const fields = {
    days: document.getElementById("days"),
    hours: document.getElementById("hours"),
    minutes: document.getElementById("minutes"),
    seconds: document.getElementById("seconds")
  };
  const pad = value => String(value).padStart(2, "0");

  function updateCountdown() {
    const remaining = target.getTime() - Date.now();
    if (remaining <= 0) {
      fields.days.textContent = "00";
      fields.hours.textContent = "00";
      fields.minutes.textContent = "00";
      fields.seconds.textContent = "00";
      document.querySelector(".eyebrow").textContent = "IT'S TIME";
      document.querySelector("h1").innerHTML = "THE MOVIE<br><em>STARTS NOW.</em>";
      return;
    }
    const totalSeconds = Math.floor(remaining / 1000);
    fields.days.textContent = String(Math.floor(totalSeconds / 86400)).padStart(3, "0");
    fields.hours.textContent = pad(Math.floor((totalSeconds % 86400) / 3600));
    fields.minutes.textContent = pad(Math.floor((totalSeconds % 3600) / 60));
    fields.seconds.textContent = pad(totalSeconds % 60);
  }

  updateCountdown();
  window.setInterval(updateCountdown, 1000);
})();