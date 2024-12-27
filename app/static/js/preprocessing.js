document.getElementById('btn-create-common-bg').addEventListener('click', function() {
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
    .then(response => {
        if (response.ok) {
            alert('Common background image created successfully for Camera ' + camera + ' Condition ' + condition + '!');
        } else {
            alert('Failed to create common background image.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while creating common background images.');
    });
});

document.getElementById('btn-create-bg').addEventListener('click', function() {
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
