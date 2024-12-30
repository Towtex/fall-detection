let extractFgFdController = new AbortController();

document.getElementById('btn-extract-fg-fd').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-fg').value;
    const camera = document.getElementById('camera-select-fg').value;
    const trial = document.getElementById('trial-select-fg').value;
    const activity = document.getElementById('activity-select-fg').value;
    console.log('Subject:', subject, 'Camera:', camera, 'Trial:', trial, 'Activity:', activity);
    extractFgFdController = new AbortController();

    // Show starting message
    alert(`Starting foreground extraction using FD for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}...`);

    const startTime = Date.now();

    fetch('/api/extract_fg_fd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity }),
        signal: extractFgFdController.signal
    })
        .then(response => {
            if (response.ok) {
                response.text().then(() => {
                    const endTime = Date.now();
                    const executionTime = ((endTime - startTime) / 1000).toFixed(2);
                    alert(`Foreground extraction using FD completed successfully for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity} in ${executionTime} seconds!`);
                });
            } else {
                alert('Failed to extract Foreground using FD.');
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('Foreground extraction using FD was aborted.');
            } else {
                console.error('Error:', error);
                alert('An error occurred while extracting FG FD.');
            }
        });
});

document.getElementById('btn-stop-extract-fg-fd').addEventListener('click', function () {
    extractFgFdController.abort();
    alert('Foreground extraction using FD has been stopped.');
});

let extractFgYoloController = new AbortController();

document.getElementById('btn-extract-fg-yolo').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-fg-yolo').value;
    const camera = document.getElementById('camera-select-fg-yolo').value;
    const trial = document.getElementById('trial-select-fg-yolo').value;
    const activity = document.getElementById('activity-select-fg-yolo').value;
    console.log('Subject:', subject, 'Camera:', camera, 'Trial:', trial, 'Activity:', activity);
    extractFgYoloController = new AbortController();

    // Show starting message
    alert(`Starting foreground extraction using YOLO for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}...`);

    const startTime = Date.now();

    fetch('/api/extract_fg_yolo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity }),
        signal: extractFgYoloController.signal
    })
        .then(response => {
            if (response.ok) {
                response.text().then(() => {
                    const endTime = Date.now();
                    const executionTime = ((endTime - startTime) / 1000).toFixed(2);
                    alert(`Foreground extraction using YOLO completed successfully for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity} in ${executionTime} seconds!`);
                });
            } else {
                alert('Failed to extract Foreground using YOLO.');
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('Foreground extraction using YOLO was aborted.');
            } else {
                console.error('Error:', error);
                alert('An error occurred while extracting FG YOLO.');
            }
        });
});

document.getElementById('btn-stop-extract-fg-yolo').addEventListener('click', function () {
    extractFgYoloController.abort();
    alert('Foreground extraction using YOLO has been stopped.');
});
