function createImageContainer(imageSrc, labelText) {
    const imgContainer = document.createElement('div');
    imgContainer.className = 'image-container';

    const img = document.createElement('img');
    img.src = imageSrc;
    img.className = 'large-image';

    const label = document.createElement('div');
    label.className = 'image-label';
    label.textContent = labelText;

    imgContainer.appendChild(img);
    imgContainer.appendChild(label);

    return imgContainer;
}

function formatImageName(imagePath) {
    const imageName = imagePath.split('/').pop().replace('.png', '').replace(/_/g, ' ');
    return imageName.replace('Subject', 'Subject_').replace('Trial', 'Trial_').replace('Activity', 'Activity_').replace('Con', 'Condition_').replace('Camera', 'Camera_').replace('background', 'background for ');
}

document.getElementById('btn-create-common-bg').addEventListener('click', function () {
    const camera = document.getElementById('camera-select-common').value;
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
                alert('Common background image created successfully for Camera: ' + camera + ' Condition: ' + condition + '!');
                const container = document.getElementById('common-bg-container');
                container.innerHTML = ''; // Clear previous images

                const formattedName = formatImageName(data.image);
                const imgContainer = createImageContainer(data.image, formattedName);
                container.appendChild(imgContainer);
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
    const camera = document.getElementById('camera-select-subject').value;
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
                alert(data.message);
                const container = document.getElementById('subject-bg-container');
                container.innerHTML = ''; // Clear previous images

                if (activity === 'all') {
                    data.images.forEach(imagePath => {
                        const formattedName = formatImageName(imagePath);
                        const imgContainer = createImageContainer(imagePath, formattedName);
                        container.appendChild(imgContainer);
                    });
                } else {
                    const formattedName = formatImageName(data.image);
                    const imgContainer = createImageContainer(data.image, formattedName);
                    container.appendChild(imgContainer);
                }
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
