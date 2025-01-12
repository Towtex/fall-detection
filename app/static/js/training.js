document.getElementById('btn-create-label').addEventListener('click', function() {
    const feature = document.getElementById('feature-select-training').value;
    const classLimit = document.getElementById('class-limit-select-training').value;
    const subject = document.getElementById('subject-select-training').value;
    const camera = document.getElementById('camera-select-training').value;

    fetch('/api/create_label', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            feature: feature,
            class_limit: classLimit,
            subject: subject,
            camera: camera
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while creating the label.');
    });
});
