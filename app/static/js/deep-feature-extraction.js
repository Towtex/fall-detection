document.getElementById('btn-extract-deep-features').addEventListener('click', function () {
    const feature = document.getElementById('method-select-deep-feature').value;
    const subject = document.getElementById('subject-select-deep-feature').value;
    const camera = document.getElementById('camera-select-deep-feature').value;
    const trial = document.getElementById('trial-select-deep-feature').value;
    const activity = document.getElementById('activity-select-deep-feature').value;

    const data = {
        feature: feature,
        subject: subject,
        camera: camera,
        trial: trial,
        activity: activity
    };
    if (camera == 3) {
        alert(`Extracting deep features for ${feature} of subject ${subject}, camera 1+2, trial ${trial}, activity ${activity}`);
    }
    else {
        alert(`Extracting deep features for ${feature} of subject ${subject}, camera ${camera}, trial ${trial}, activity ${activity}`);
    }
    fetch('/api/extract_deep_features', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.text())
        .then(text => {
            alert(text);
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`Error: ${error}`);
        });
});

document.getElementById('btn-stop-deep-extraction').addEventListener('click', function () {
    fetch('/api/stop_extract_deep_features', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`Error: ${error}`);
        });
});
