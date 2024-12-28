document.getElementById('btn-create-common-bg').addEventListener('click', function () {
    const camera = document.getElementById('camera-select').value;
    const condition = document.getElementById('condition-select').value;
    console.log('Camera:', camera, 'Condition:', condition);
    fetch('/api/create_common_background', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ camera: camera, condition: condition })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Common background image created successfully for Camera ' + camera + ' Condition ' + condition + '!');
                const container = document.getElementById('common-bg-container');
                container.innerHTML = ''; // Clear previous images

                data.images.forEach(imagePath => {
                    const imgContainer = document.createElement('div');
                    imgContainer.className = 'image-container';

                    const img = document.createElement('img');
                    img.src = imagePath; // Image source from backend
                    img.className = 'medium-image';

                    const label = document.createElement('div');
                    label.className = 'image-label';
                    label.textContent = imagePath.split('/').pop(); // Display the image name

                    imgContainer.appendChild(img);
                    imgContainer.appendChild(label);
                    container.appendChild(imgContainer);
                });
            } else {
                alert('Failed to create common background image.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while creating common background images.');
        });
});

document.getElementById('btn-clear-common-bg').addEventListener('click', function () {
    document.getElementById('common-bg-container').innerHTML = '';
    const hr = document.querySelector('#common-bg-container').previousElementSibling;
    if (hr && hr.tagName === 'HR') hr.remove();
});

document.getElementById('btn-create-subject-bg').addEventListener('click', function () {
    const subject = document.getElementById('subject-select').value;
    console.log('Subject:', subject);
    fetch('/api/create_background', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Background images created successfully for Subject ' + subject + '!');
                const container = document.getElementById('subject-bg-container');
                container.innerHTML = ''; // Clear previous images

                data.images.forEach(imagePath => {
                    const imgContainer = document.createElement('div');
                    imgContainer.className = 'image-container';

                    const img = document.createElement('img');
                    img.src = imagePath; // Image source from backend
                    img.className = 'small-image';

                    const label = document.createElement('div');
                    label.className = 'image-label';
                    label.textContent = imagePath.split('/').pop(); // Display the image name

                    imgContainer.appendChild(img);
                    imgContainer.appendChild(label);
                    container.appendChild(imgContainer);
                });
            } else {
                alert('Failed to create background images.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while creating background images.');
        });
});

document.getElementById('btn-clear-subject-bg').addEventListener('click', function () {
    document.getElementById('subject-bg-container').innerHTML = '';
    const hr = document.querySelector('#subject-bg-container').previousElementSibling;
    if (hr && hr.tagName === 'HR') hr.remove();
});

let extractFgFdController = new AbortController();

document.getElementById('btn-extract-fg-fd').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-fg').value;
    console.log('Subject:', subject);
    extractFgFdController = new AbortController();
    fetch('/api/extract_fg_fd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject }),
        signal: extractFgFdController.signal
    })
        .then(response => {
            if (response.ok) {
                alert('Foreground extraction using FD completed successfully for Subject ' + subject + '!');
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
});
