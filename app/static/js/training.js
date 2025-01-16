document.getElementById('btn-create-label').addEventListener('click', function () {
    const feature = document.getElementById('feature-select-create-label').value;
    const classLimit = document.getElementById('class-limit-select-create-label').value;
    const subject = document.getElementById('subject-select-create-label').value;
    const camera = document.getElementById('camera-select-create-label').value;

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

document.getElementById('btn-start-training').addEventListener('click', function () {
    const feature = document.getElementById('feature-select-training').value;
    const classLimit = document.getElementById('class-limit-select-training').value;
    const camera = document.getElementById('camera-select-training').value;
    alert(`Training started for ${feature} with classes: ${classLimit} and camera: ${camera}.`);

    const loadingCircleContainer = document.createElement('div');
    loadingCircleContainer.id = 'loading-circle';
    loadingCircleContainer.className = 'd-flex align-items-center';
    loadingCircleContainer.style = 'margin-top: 1rem;';

    const spinner = document.createElement('div');
    spinner.className = 'spinner-border';
    spinner.role = 'status';
    spinner.style = 'margin-right: 1rem;';

    const strongText = document.createElement('strong');
    strongText.textContent = 'Training...';

    loadingCircleContainer.appendChild(spinner);
    loadingCircleContainer.appendChild(strongText);

    document.querySelector('.d-flex.justify-content-center.align-items-center').appendChild(loadingCircleContainer);

    fetch('/api/start_training', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            feature: feature,
            class_limit: classLimit,
            camera: camera
        }),
    })
        .then(response => response.text())
        .then(data => {
            document.getElementById('loading-circle').remove();
            const endTime = Date.now();
            const executionTime = (endTime - startTime) / 1000;
            alert(`${data}\nExecution time: ${executionTime} seconds`);
        })
        .catch(error => {
            document.getElementById('loading-circle').remove();
            console.error('Error:', error);
            alert('An error occurred while starting the training.');
        });
});

document.getElementById('btn-stop-training').addEventListener('click', function () {
    fetch('/api/stop_training', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            const loadingCircle = document.getElementById('loading-circle');
            if (loadingCircle) {
                loadingCircle.remove();
            }
            alert(data.message);
        })
        .catch(error => {
            const loadingCircle = document.getElementById('loading-circle');
            if (loadingCircle) {
                loadingCircle.remove();
            }
            console.error('Error:', error);
            alert('An error occurred while stopping the training.');
        });
});


