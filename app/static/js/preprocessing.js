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
                    label.textContent = imagePath.split('/').pop().replace('.png', ''); // Display the image name

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
});

document.getElementById('btn-create-subject-bg').addEventListener('click', function () {
    const subject = document.getElementById('subject-select').value;
    const camera = document.getElementById('camera-select').value;
    const trial = document.getElementById('trial-select').value;
    const activity = document.getElementById('activity-select').value;
    console.log('Subject:', subject, 'Camera:', camera, 'Trial:', trial, 'Activity:', activity);
    fetch('/api/create_background', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject, camera: camera, trial: trial, activity: activity })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Background image created successfully for Subject ' + subject + ' Camera ' + camera + ' Trial ' + trial + ' Activity ' + activity + '!');
                const container = document.getElementById('subject-bg-container');
                container.innerHTML = ''; // Clear previous images

                const imgContainer = document.createElement('div');
                imgContainer.className = 'image-container';

                const img = document.createElement('img');
                img.src = data.image; // Image source from backend
                img.className = 'large-image';

                const label = document.createElement('div');
                label.className = 'image-label';
                label.textContent = data.image.split('/').pop().replace('.png', '').replace(/_/g, ' '); // Display the image name without .png and replace underscores with spaces

                imgContainer.appendChild(img);
                imgContainer.appendChild(label);
                container.appendChild(imgContainer);
            } else {
                alert('Failed to create background image.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while creating background image.');
        });
});

document.getElementById('btn-clear-subject-bg').addEventListener('click', function () {
    document.getElementById('subject-bg-container').innerHTML = '';
});
