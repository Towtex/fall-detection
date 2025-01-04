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
        .then(response => response.text())
        .then(text => {
            console.log(text);
            if (text.includes("Error:")) {
                alert(`${text}`);
            } else {
                const endTime = Date.now();
                const executionTime = ((endTime - startTime) / 1000).toFixed(2);
                alert(`Foreground extraction using FD completed for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity} in ${executionTime} seconds!`);
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('Foreground extraction using FD was aborted.');
            } else {
                console.error('Error:', error);
                alert(`An error occurred while extracting FG FD: ${error.message}`);
            }
        });
});

document.getElementById('btn-stop-extract-fg-fd').addEventListener('click', function () {
    fetch('/api/stop_extract_fg_fd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                alert('Foreground extraction using FD has been stopped.');
            } else {
                alert('Failed to stop foreground extraction using FD.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while stopping FG FD extraction.');
        });
});

document.getElementById('btn-result-fg-fd').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-fg').value;
    const camera = document.getElementById('camera-select-fg').value;
    const trial = document.getElementById('trial-select-fg').value;
    const activity = document.getElementById('activity-select-fg').value;

    if (trial === 'all') {
        alert('Please select a specific trial.');
        return;
    }

    if (activity === 'all') {
        fetch('/api/get_fg_fd_videos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject: subject, camera: camera, trial: trial })
        })
            .then(response => response.json())
            .then(data => {
                const videosContainer = document.getElementById('videos-container');
                videosContainer.innerHTML = ''; // Clear previous videos
                if (data.videos && data.videos.length > 0) {
                    data.videos.forEach((video_url, index) => {
                        const videoWrapper = document.createElement('div');
                        videoWrapper.style.marginBottom = '1rem'; // Add space between videos
                        const label = document.createElement('p');
                        label.textContent = `Activity ${index + 1}`;
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
                        videosContainer.appendChild(videoWrapper);
                    });
                    const existingTitle = videosContainer.querySelector('h3');
                    if (existingTitle) {
                        videosContainer.removeChild(existingTitle);
                    }
                    const title = document.createElement('h3');
                    title.textContent = `FG FD, Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: All`;
                    videosContainer.insertBefore(title, videosContainer.firstChild);
                    videosContainer.style.display = 'block';
                    document.getElementById('video-container').style.display = 'none';
                } else {
                    alert('No videos found.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching the videos.');
            });
    } else {
        fetch('/api/get_fg_fd_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity })
        })
            .then(response => response.json())
            .then(data => {
                if (data.video_url) {
                    const videoSource = document.getElementById('videoSource');
                    videoSource.src = data.video_url;
                    const video = document.getElementById('extractedVideo');
                    video.load();
                    video.play();
                    const videoContainer = document.getElementById('video-container');
                    const existingTitle = videoContainer.querySelector('h3');
                    if (existingTitle) {
                        videoContainer.removeChild(existingTitle);
                    }
                    const title = document.createElement('h3');
                    title.textContent = `FD FD, Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}`;
                    videoContainer.insertBefore(title, videoContainer.firstChild);
                    videoContainer.style.display = 'block';
                    document.getElementById('videos-container').style.display = 'none';
                } else {
                    alert('No video found.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching the video.');
            });
    }
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
        .then(response => response.text())
        .then(text => {
            console.log(text);
            if (text.includes("Error:")) {
                alert(`${text}`);
            } else {
                const endTime = Date.now();
                const executionTime = ((endTime - startTime) / 1000).toFixed(2);
                alert(`Foreground extraction using YOLO completed for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity} in ${executionTime} seconds!`);
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('Foreground extraction using YOLO was aborted.');
            } else {
                console.error('Error:', error);
                alert(`An error occurred while extracting FG YOLO: ${error.message}`);
            }
        });
});

document.getElementById('btn-stop-extract-fg-yolo').addEventListener('click', function () {
    fetch('/api/stop_extract_fg_yolo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                alert('Foreground extraction using YOLO has been stopped.');
            } else {
                alert('Failed to stop foreground extraction using YOLO.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while stopping FG YOLO extraction.');
        });
});

document.getElementById('btn-result-fg-yolo').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-fg-yolo').value;
    const camera = document.getElementById('camera-select-fg-yolo').value;
    const trial = document.getElementById('trial-select-fg-yolo').value;
    const activity = document.getElementById('activity-select-fg-yolo').value;

    if (trial === 'all') {
        alert('Please select a specific trial.');
        return;
    }

    if (activity === 'all') {
        fetch('/api/get_fg_yolo_videos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject: subject, camera: camera, trial: trial })
        })
            .then(response => response.json())
            .then(data => {
                const videosContainer = document.getElementById('videos-container');
                videosContainer.innerHTML = ''; // Clear previous videos
                if (data.videos && data.videos.length > 0) {
                    data.videos.forEach((video_url, index) => {
                        const videoWrapper = document.createElement('div');
                        videoWrapper.style.marginBottom = '1rem'; // Add space between videos
                        const label = document.createElement('p');
                        label.textContent = `Activity ${index + 1}`;
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
                        videosContainer.appendChild(videoWrapper);
                    });
                    const existingTitle = videosContainer.querySelector('h3');
                    if (existingTitle) {
                        videosContainer.removeChild(existingTitle);
                    }
                    const title = document.createElement('h3');
                    title.textContent = `FG Yolo, Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: All`;
                    videosContainer.insertBefore(title, videosContainer.firstChild);
                    videosContainer.style.display = 'block';
                    document.getElementById('video-container').style.display = 'none';
                } else {
                    alert('No videos found.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching the videos.');
            });
    } else {
        fetch('/api/get_fg_yolo_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity })
        })
            .then(response => response.json())
            .then(data => {
                if (data.video_url) {
                    const videoSource = document.getElementById('videoSource');
                    videoSource.src = data.video_url;
                    const video = document.getElementById('extractedVideo');
                    video.load();
                    video.play();
                    const videoContainer = document.getElementById('video-container');
                    const existingTitle = videoContainer.querySelector('h3');
                    if (existingTitle) {
                        videoContainer.removeChild(existingTitle);
                    }
                    const title = document.createElement('h3');
                    title.textContent = `FG Yolo, Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}`;
                    videoContainer.insertBefore(title, videoContainer.firstChild);
                    videoContainer.style.display = 'block';
                    document.getElementById('videos-container').style.display = 'none';
                } else {
                    alert('No video found.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching the video.');
            });
    }
});

let createShiController = new AbortController();

document.getElementById('btn-create-shi').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-shi').value;
    const camera = document.getElementById('camera-select-shi').value;
    const trial = document.getElementById('trial-select-shi').value;
    const activity = document.getElementById('activity-select-shi').value;
    const method = document.getElementById('method-select-shi').value;
    console.log('Subject:', subject, 'Camera:', camera, 'Trial:', trial, 'Activity:', activity, 'Method:', method);
    createShiController = new AbortController();

    // Show starting message
    alert(`Starting SHI creation for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}, Method: ${method}...`);

    const startTime = Date.now();

    fetch('/api/create_shi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity, method: method }),
        signal: createShiController.signal
    })
        .then(response => response.text())
        .then(text => {
            console.log(text);
            if (text.includes("Error:")) {
                alert(`${text}`);
            } else {
                const endTime = Date.now();
                const executionTime = ((endTime - startTime) / 1000).toFixed(2);
                alert(`SHI creation completed for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}, Method: ${method} in ${executionTime} seconds!`);
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('SHI creation was aborted.');
            } else {
                console.error('Error:', error);
                alert(`An error occurred while creating SHI: ${error.message}`);
            }
        });
});

document.getElementById('btn-stop-create-shi').addEventListener('click', function () {
    fetch('/api/stop_create_shi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                alert('SHI creation has been stopped.');
            } else {
                alert('Failed to stop SHI creation.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while stopping SHI creation.');
        });
});

let extractDofController = new AbortController();

document.getElementById('btn-extract-dof').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-dof').value;
    const camera = document.getElementById('camera-select-dof').value;
    const trial = document.getElementById('trial-select-dof').value;
    const activity = document.getElementById('activity-select-dof').value;
    console.log('Subject:', subject, 'Camera:', camera, 'Trial:', trial, 'Activity:', activity);
    extractDofController = new AbortController();

    // Show starting message
    alert(`Starting DOF extraction for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}...`);

    const startTime = Date.now();

    fetch('/api/extract_dof', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity }),
        signal: extractDofController.signal
    })
        .then(response => response.text())
        .then(text => {
            console.log(text);
            if (text.includes("Error:")) {
                alert(`${text}`);
            } else {
                const endTime = Date.now();
                const executionTime = ((endTime - startTime) / 1000).toFixed(2);
                alert(`DOF extraction completed for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity} in ${executionTime} seconds!`);
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('DOF extraction was aborted.');
            } else {
                console.error('Error:', error);
                alert(`An error occurred while extracting DOF: ${error.message}`);
            }
        });
});

document.getElementById('btn-stop-extract-dof').addEventListener('click', function () {
    fetch('/api/stop_extract_dof', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                alert('DOF extraction has been stopped.');
            } else {
                alert('Failed to stop DOF extraction.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while stopping DOF extraction.');
        });
});

let createDofShiController = new AbortController();

document.getElementById('btn-create-dof-shi').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-dof-shi').value;
    const camera = document.getElementById('camera-select-dof-shi').value;
    const trial = document.getElementById('trial-select-dof-shi').value;
    const activity = document.getElementById('activity-select-dof-shi').value;
    const method = document.getElementById('method-select-dof-shi').value;
    console.log('Subject:', subject, 'Camera:', camera, 'Trial:', trial, 'Activity:', activity, 'Method:', method);
    createDofShiController = new AbortController();

    // Show starting message
    alert(`Starting DOF SHI creation for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}, Method: ${method}...`);

    const startTime = Date.now();

    fetch('/api/create_dof_shi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity, method: method }),
        signal: createDofShiController.signal
    })
        .then(response => response.text())
        .then(text => {
            console.log(text);
            if (text.includes("Error:")) {
                alert(`${text}`);
            } else {
                const endTime = Date.now();
                const executionTime = ((endTime - startTime) / 1000).toFixed(2);
                alert(`DOF SHI creation completed for Subject: ${subject}, Camera: ${camera}, Trial: ${trial}, Activity: ${activity}, Method: ${method} in ${executionTime} seconds!`);
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('DOF SHI creation was aborted.');
            } else {
                console.error('Error:', error);
                alert(`An error occurred while creating DOF SHI: ${error.message}`);
            }
        });
});

document.getElementById('btn-stop-create-dof-shi').addEventListener('click', function () {
    fetch('/api/stop_create_dof_shi', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (response.ok) {
                alert('DOF SHI creation has been stopped.');
            } else {
                alert('Failed to stop DOF SHI creation.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while stopping DOF SHI creation.');
        });
});

document.getElementById('btn-clear-videos').addEventListener('click', function () {
    document.getElementById('video-container').style.display = 'none';
    document.getElementById('videos-container').style.display = 'none';
    document.getElementById('videos-container').innerHTML = '';
});