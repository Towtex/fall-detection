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
    loadingCircleContainer.className = 'd-flex flex-column align-items-center';
    loadingCircleContainer.style = 'margin-top: 1rem;';

    const spinner = document.createElement('div');
    spinner.className = 'spinner-border';
    spinner.role = 'status';
    spinner.style = 'margin-bottom: 1rem;';

    const strongText = document.createElement('strong');
    strongText.textContent = 'Training...';

    const runningTime = document.createElement('div');
    runningTime.id = 'running-time';
    runningTime.style = 'margin-top: 1rem;';

    loadingCircleContainer.appendChild(spinner);
    loadingCircleContainer.appendChild(strongText);
    loadingCircleContainer.appendChild(runningTime);

    document.querySelector('.d-flex.justify-content-center.align-items-center').appendChild(loadingCircleContainer);

    const startTime = Date.now();
    const intervalId = setInterval(() => {
        const currentTime = Date.now();
        const elapsedTime = ((currentTime - startTime) / 1000).toFixed(0);
        document.getElementById('running-time').textContent = `${elapsedTime} seconds`;
    }, 1000);

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
            clearInterval(intervalId);
            document.getElementById('loading-circle').remove();
            const endTime = Date.now();
            const executionTime = ((endTime - startTime) / 1000).toFixed(2);
            alert(`${data}\nExecution time: ${executionTime} seconds`);
        })
        .catch(error => {
            clearInterval(intervalId);
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

document.getElementById('btn-create-label-loocv').addEventListener('click', function () {
    const feature = document.getElementById('feature-select-create-label-loocv').value;
    const classLimit = document.getElementById('class-limit-select-create-label-loocv').value;
    const subject = document.getElementById('subject-select-create-label-loocv').value;
    const camera = document.getElementById('camera-select-create-label-loocv').value;

    fetch('/api/create_label_loocv', {
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
            alert('An error occurred while creating the LOOCV label.');
        });
});

document.getElementById('btn-start-training-loocv').addEventListener('click', function () {
    const feature = document.getElementById('feature-select-training-loocv').value;
    const classLimit = document.getElementById('class-limit-select-training-loocv').value;
    const camera = document.getElementById('camera-select-training-loocv').value;
    alert(`LOOCV Training started for ${feature} with classes: ${classLimit} and camera: ${camera}.`);

    const loadingCircleContainer = document.createElement('div');
    loadingCircleContainer.id = 'loading-circle-loocv';
    loadingCircleContainer.className = 'd-flex flex-column align-items-center';
    loadingCircleContainer.style = 'margin-top: 1rem;';

    const spinner = document.createElement('div');
    spinner.className = 'spinner-border';
    spinner.role = 'status';
    spinner.style = 'margin-bottom: 1rem;';

    const strongText = document.createElement('strong');
    strongText.textContent = 'Training...';

    const runningTime = document.createElement('div');
    runningTime.id = 'running-time-loocv';
    runningTime.style = 'margin-top: 1rem;';

    loadingCircleContainer.appendChild(spinner);
    loadingCircleContainer.appendChild(strongText);
    loadingCircleContainer.appendChild(runningTime);

    document.querySelector('.d-flex.justify-content-center.align-items-center').appendChild(loadingCircleContainer);

    const startTime = Date.now();
    const intervalId = setInterval(() => {
        const currentTime = Date.now();
        const elapsedTime = ((currentTime - startTime) / 1000).toFixed(2);
        document.getElementById('running-time-loocv').textContent = `Running time: ${elapsedTime} seconds`;
    }, 1000);

    fetch('/api/start_training_loocv', {
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
            clearInterval(intervalId);
            document.getElementById('loading-circle-loocv').remove();
            const endTime = Date.now();
            const executionTime = ((endTime - startTime) / 1000).toFixed(2);
            alert(`${data}\nExecution time: ${executionTime} seconds`);
        })
        .catch(error => {
            clearInterval(intervalId);
            document.getElementById('loading-circle-loocv').remove();
            console.error('Error:', error);
            alert('An error occurred while starting the LOOCV training.');
        });
});

document.getElementById('btn-stop-training-loocv').addEventListener('click', function () {
    fetch('/api/stop_training_loocv', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            const loadingCircle = document.getElementById('loading-circle-loocv');
            if (loadingCircle) {
                loadingCircle.remove();
            }
            alert(data.message);
        })
        .catch(error => {
            const loadingCircle = document.getElementById('loading-circle-loocv');
            if (loadingCircle) {
                loadingCircle.remove();
            }
            console.error('Error:', error);
            alert('An error occurred while stopping the LOOCV training.');
        });
});


