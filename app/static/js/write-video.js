document.addEventListener('DOMContentLoaded', function () {
    const btnWriteVideoTrial3 = document.getElementById('btn-result-write-video-trial3');
    const btnWriteVideoLoocv = document.getElementById('btn-result-write-video-loocv');
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

    btnClearResult.addEventListener('click', function () {
        resultsContainer.style.display = 'none';
        resultsContent.innerHTML = '';
    });

    function displayResults(data) {
        resultsContainer.style.display = 'block';
        resultsHeader.textContent = 'Write Video Results';
        resultsContent.innerHTML = `<div class="alert alert-info">${data.message}</div>`;
    }
});
