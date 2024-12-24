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
            alert('Common background created successfully for Camera ' + camera + ' Condition ' + condition + '!');
        } else {
            alert('Failed to create common background.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while starting preprocessing.');
    });
});
