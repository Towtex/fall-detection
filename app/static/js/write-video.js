document.addEventListener('DOMContentLoaded', function () {
    const btnWriteVideoTrial3 = document.getElementById('btn-write-video-trial3');
    const btnWriteVideoLoocv = document.getElementById('btn-write-video-loocv');
    const btnResultWriteVideoTrial3 = document.getElementById('btn-result-write-video-trial3');
    const btnResultWriteVideoLoocv = document.getElementById('btn-result-write-video-loocv');
    const btnClearResult = document.getElementById('btn-clear');
    const resultsContainer = document.getElementById('results-container');
    const resultsHeader = document.getElementById('results-header');
    const resultsContent = document.getElementById('results-content');

    btnWriteVideoTrial3.addEventListener('click', function () {
        const subject = document.getElementById('subject-select-write-video-trial3').value;
        const camera = document.getElementById('camera-select-write-video-trial3').value;
        const feature = document.getElementById('feature-select-write-video-trial3').value;
        const classLimit = document.getElementById('class-limit-select-write-video-trial3').value;
        const action = document.getElementById('activity-select-write-video-trial3').value;
        const requestBody = JSON.stringify({
            subject: subject,
            camera: camera,
            feature: feature,
            class_limit: classLimit,
            action: action
        });
        alert('Writing video started. Please wait for the results.');
        console.log(requestBody);
        fetch('/api/write_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: requestBody
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                displayResults(data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });

    btnWriteVideoLoocv.addEventListener('click', function () {
        const subject = document.getElementById('subject-select-write-video-loocv').value;
        const camera = document.getElementById('camera-select-write-video-loocv').value;
        const feature = document.getElementById('feature-select-write-video-loocv').value;
        const classLimit = document.getElementById('class-limit-select-write-video-loocv').value;
        const trial = document.getElementById('trial-select-write-video-loocv').value;
        const action = document.getElementById('activity-select-write-video-loocv').value;
        const requestBody = JSON.stringify({
            subject: subject,
            camera: camera,
            feature: feature,
            class_limit: classLimit,
            loocv: true,
            trial: trial,
            action: action
        });
        alert('Writing video for LOOCV started. Please wait for the results.');
        console.log(requestBody);
        fetch('/api/write_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: requestBody
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                displayResults(data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });

    btnResultWriteVideoTrial3.addEventListener('click', function () {
        const subject = document.getElementById('subject-select-write-video-trial3').value;
        const camera = document.getElementById('camera-select-write-video-trial3').value;
        const feature = document.getElementById('feature-select-write-video-trial3').value;
        const classLimit = document.getElementById('class-limit-select-write-video-trial3').value;
        const action = document.getElementById('activity-select-write-video-trial3').value;

        fetch('/api/get_video_result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject: subject, camera: camera, feature: feature, class_limit: classLimit, action: action })
        })
            .then(response => response.json())
            .then(data => {
                displayVideoResults(data, `Trial 3, Subject: ${subject}, Camera: ${camera}, Feature: ${feature}, Class Limit: ${classLimit}, Activity: ${action}`);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching the video results.');
            });
    });

    btnResultWriteVideoLoocv.addEventListener('click', function () {
        const subject = document.getElementById('subject-select-write-video-loocv').value;
        const camera = document.getElementById('camera-select-write-video-loocv').value;
        const feature = document.getElementById('feature-select-write-video-loocv').value;
        const classLimit = document.getElementById('class-limit-select-write-video-loocv').value;
        const trial = document.getElementById('trial-select-write-video-loocv').value;
        const action = document.getElementById('activity-select-write-video-loocv').value;

        fetch('/api/get_video_result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject: subject, camera: camera, feature: feature, class_limit: classLimit, loocv: true, trial: trial, action: action })
        })
            .then(response => response.json())
            .then(data => {
                displayVideoResults(data, `LOOCV, Subject: ${subject}, Camera: ${camera}, Feature: ${feature}, Class Limit: ${classLimit}, Trial: ${trial}, Activity: ${action}`);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching the video results.');
            });
    });

    btnClearResult.addEventListener('click', function () {
        resultsContainer.style.display = 'none';
        resultsContent.innerHTML = '';
    });

    function displayResults(data) {
        resultsContainer.style.display = 'block';
        resultsHeader.textContent = 'Video Results';
        resultsContent.innerHTML = `<div class="alert alert-info">${data.message}</div>`;
    }

    function displayVideoResults(data, title) {
        resultsContainer.style.display = 'block';
        resultsHeader.textContent = title;
        resultsContent.innerHTML = '';

        if (data.videos && data.videos.length > 0) {
            data.videos.forEach((video_url, index) => {
                const videoWrapper = document.createElement('div');
                videoWrapper.style.marginBottom = '1rem'; // Add space between videos
                const label = document.createElement('p');
                label.textContent = `Video ${index + 1}`;
                const videoElement = document.createElement('video');
                videoElement.width = 320;
                videoElement.height = 240;
                videoElement.loop = true;
                videoElement.autoplay = true;
                videoElement.controls = true;
                const sourceElement = document.createElement('source');
                sourceElement.src = video_url;
                sourceElement.type = 'video/mp4';
                videoElement.appendChild(sourceElement);
                videoWrapper.appendChild(videoElement);
                videoWrapper.appendChild(label);
                resultsContent.appendChild(videoWrapper);
            });
        } else {
            resultsContent.innerHTML = '<div class="alert alert-warning">No videos found.</div>';
        }
    }
});
