document.addEventListener("DOMContentLoaded", () => {
  const transcriptionContainer = document.getElementById(
    "transcription-container"
  );
  const transcriptionView = document.getElementById("transcription-view");
  const timelineView = document.getElementById("timeline-view");
  const timestampLabel = document.getElementById("timestamp-label");
  const hourMarksContainer = document.getElementById("hour-marks-container");
  const hourMarksView = document.getElementById("hour-marks-view");
  const focusedImage = document.getElementById("focused-image");

  // Sizer divs to create the scrollable height/width
  const transcriptionSizer = document.createElement("div");
  transcriptionSizer.style.position = "relative";
  transcriptionView.appendChild(transcriptionSizer);
  const hourMarksSizer = document.createElement("div");
  hourMarksSizer.style.position = "relative";
  hourMarksView.appendChild(hourMarksSizer);
  const timelineSizer = document.createElement("div");
  timelineSizer.style.position = "relative";
  timelineSizer.style.height = "100%"; // Fix for image container height
  timelineView.appendChild(timelineSizer);

  let transcriptionElements = [];
  let imageElements = [];
  let logData = [];
  let startTime, endTime;
  let totalDurationSeconds = 0;
  const PIXELS_PER_SECOND_VERTICAL = 20;
  const PIXELS_PER_SECOND_HORIZONTAL = 10;

  let requestedLogFile = window.location.pathname.substring(1); // Get filename from URL
  fetch(`/api/gobi-log/${requestedLogFile}`)
    .then((response) => response.json())
    .then((rawData) => {
      if (rawData.error) {
        transcriptionView.innerHTML = `<p>Error loading log data: ${rawData.error}</p>`;
        return;
      }

      // Process and group transcriptions
      const processedData = [];
      let lastItem = null;
      rawData.forEach((item) => {
        if (item.type === "transcription") {
          if (
            lastItem &&
            lastItem.type === "transcription" &&
            lastItem.timestamp === item.timestamp
          ) {
            lastItem.content += ` => ${item.content}`;
          } else {
            // Ensure a clean object is pushed
            const newItem = {
              timestamp: item.timestamp,
              type: item.type,
              content: item.content,
            };
            processedData.push(newItem);
            lastItem = newItem;
          }
        } else {
          processedData.push(item);
          lastItem = item;
        }
      });

      logData = processedData.map((item) => ({
        ...item,
        date: new Date(item.timestamp),
      }));
      if (logData.length > 1) {
        startTime = logData[0].date;
        endTime = logData[logData.length - 1].date;
        totalDurationSeconds = (endTime - startTime) / 1000;
      }
      renderLog(logData);
      renderTimeMarks();
      setupScrollSync();
    })
    .catch((error) => {
      console.error("Error fetching gobi log:", error);
      transcriptionView.innerHTML = "<p>Error loading log data.</p>";
    });

  function renderLog(data) {
    const transcriptionFragment = document.createDocumentFragment();
    const timelineFragment = document.createDocumentFragment();

    // Set the total scrollable height
    const totalPixelHeight = totalDurationSeconds * PIXELS_PER_SECOND_VERTICAL;
    transcriptionSizer.style.height = `${totalPixelHeight}px`;

    // Set the total scrollable width for the timeline
    const totalPixelWidth = totalDurationSeconds * PIXELS_PER_SECOND_HORIZONTAL;
    timelineSizer.style.width = `${totalPixelWidth}px`;

    data.forEach((item) => {
      if (item.type === "transcription") {
        const p = document.createElement("p");
        p.className = "transcription-item";
        p.textContent = `[${item.timestamp.split(" ")[1]}] ${item.content}`;
        p.dataset.timestamp = item.timestamp;

        // Position based on time
        const timeOffsetSeconds = (item.date - startTime) / 1000;
        p.style.top = `${timeOffsetSeconds * PIXELS_PER_SECOND_VERTICAL}px`;

        transcriptionFragment.appendChild(p);
      } else if (item.type === "image") {
        const imgContainer = document.createElement("div");
        imgContainer.className = "image-container";

        const img = document.createElement("img");
        img.src = item.path;
        img.dataset.timestamp = item.timestamp;

        const timestampEl = document.createElement("div");
        timestampEl.className = "image-timestamp";
        timestampEl.textContent = item.timestamp.split(" ")[1];

        imgContainer.appendChild(img);
        imgContainer.appendChild(timestampEl);

        // Position based on time
        const timeOffsetSeconds = (item.date - startTime) / 1000;
        imgContainer.style.left = `${
          timeOffsetSeconds * PIXELS_PER_SECOND_HORIZONTAL
        }px`;

        timelineFragment.appendChild(imgContainer);
      }
    });

    // Append to the sizer, not the view itself
    transcriptionSizer.appendChild(transcriptionFragment);
    timelineSizer.appendChild(timelineFragment);

    transcriptionElements = Array.from(
      transcriptionSizer.querySelectorAll(".transcription-item")
    );
    imageElements = Array.from(
      timelineSizer.querySelectorAll(".image-container")
    );
  }

  function renderTimeMarks() {
    if (!startTime || !endTime) return;

    const totalPixelHeight = totalDurationSeconds * PIXELS_PER_SECOND_VERTICAL;
    hourMarksSizer.style.height = `${totalPixelHeight}px`;

    const fragment = document.createDocumentFragment();

    let currentHour = new Date(startTime);
    currentHour.setMilliseconds(0);
    currentHour.setSeconds(currentHour.getSeconds() + 1);

    while (currentHour <= endTime) {
      const timeOffsetSeconds = (currentHour - startTime) / 1000;
      const topPosition = timeOffsetSeconds * PIXELS_PER_SECOND_VERTICAL;

      const mark = document.createElement("div");
      mark.classList.add("time-mark");

      const seconds = currentHour.getSeconds();
      const minutes = currentHour.getMinutes();
      const hours = currentHour.getHours();

      const timeString = `${String(hours).padStart(2, "0")}:${String(
        minutes
      ).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

      if (seconds === 0) {
        mark.classList.add("minute-mark");
        mark.dataset.time = timeString;
      } else if (seconds % 10 === 0) {
        mark.classList.add("ten-second-mark");
        mark.dataset.time = timeString;
      } else {
        mark.classList.add("second-mark");
      }

      mark.style.top = `${topPosition}px`;
      fragment.appendChild(mark);

      currentHour.setSeconds(currentHour.getSeconds() + 1);
    }

    hourMarksSizer.appendChild(fragment);
  }

  function setupScrollSync() {
    transcriptionView.addEventListener("scroll", updateViews);
  }

  function updateViews() {
    if (!startTime || !endTime) return;

    // 1. Calculate the current time based on the vertical scroll position
    const centerOffset = transcriptionView.scrollTop;
    const currentTime = new Date(
      startTime.getTime() + (centerOffset / PIXELS_PER_SECOND_VERTICAL) * 1000
    );

    // 2. Update the timestamp label
    timestampLabel.textContent = currentTime.toLocaleTimeString();

    // 3. Sync the hour marks panel
    hourMarksView.scrollTop = transcriptionView.scrollTop;

    // 4. Calculate the correct scroll position for the image timeline based on time
    const timeOffsetSeconds = (currentTime - startTime) / 1000;
    const timelineScrollLeft = timeOffsetSeconds * PIXELS_PER_SECOND_HORIZONTAL;
    timelineView.scrollLeft = timelineScrollLeft;

    // 5. Find and highlight the active image
    let activeImage = null;
    for (let i = imageElements.length - 1; i >= 0; i--) {
      const imageTimestamp = new Date(
        imageElements[i].querySelector("img").dataset.timestamp
      );
      if (imageTimestamp <= currentTime) {
        activeImage = imageElements[i];
        break;
      }
    }

    imageElements.forEach((container) => {
      container.classList.toggle("highlighted", container === activeImage);
    });

    if (activeImage) {
      const activeImageSrc = activeImage.querySelector("img").src;
      focusedImage.src = activeImageSrc;
      focusedImage.classList.add("visible");
    } else {
      focusedImage.classList.remove("visible");
    }
  }
});
