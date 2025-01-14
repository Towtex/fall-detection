document.getElementById('btn-test-model').addEventListener('click', function() {
    const feature = document.getElementById('feature-select-testing').value;
    const classLimit = document.getElementById('class-limit-select-testing').value;
    const camera = document.getElementById('camera-select-testing').value;
    const requestBody = JSON.stringify({
        feature: feature,
        class_limit: classLimit,
        camera: camera
    })
    console.log(requestBody)
    fetch('/api/start-testing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
