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
                const imgContainer = document.createElement('div');
                imgContainer.className = 'image-container';

                const img = document.createElement('img');
                img.src = `/output/common_background_images/background_Camera${camera}_Con${condition}.png`;
                img.className = 'medium-image';

                const label = document.createElement('div');
                label.className = 'image-label';
                label.textContent = `Camera ${camera} - Condition ${condition}`;

                imgContainer.appendChild(img);
                imgContainer.appendChild(label);
                document.getElementById('common-bg-container').appendChild(imgContainer);
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
    console.log('Subject:', subject);
    fetch('/api/create_background', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject })
    })
        .then(response => {
            if (response.ok) {
                alert('Background images created successfully for Subject ' + subject + '!');
            } else {
                alert('Failed to create background images.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while creating background images.');
        });
});

document.getElementById('btn-extract-fg-fd').addEventListener('click', function () {
    const subject = document.getElementById('subject-select-fg').value;
    console.log('Subject:', subject);
    fetch('/api/extract_fg_fd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ subject: subject })
    })
        .then(response => {
            if (response.ok) {
                alert('Foreground extraction using FD completed successfully for Subject ' + subject + '!');
            } else {
                alert('Failed to extract Foreground using FD.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while extracting FG FD.');
        });
});
