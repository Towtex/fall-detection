document.addEventListener('DOMContentLoaded', function () {
    const btnTestModel = document.getElementById('btn-test-model');
    const btnShowResult = document.getElementById('btn-result-test-model');
    const btnClearResult = document.getElementById('btn-clear-test-model');
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');

    btnTestModel.addEventListener('click', function () {
        const feature = document.getElementById('feature-select-testing').value;
        const classLimit = document.getElementById('class-limit-select-testing').value;
        const camera = document.getElementById('camera-select-testing').value;
        const requestBody = JSON.stringify({
            feature: feature,
            class_limit: classLimit,
            camera: camera
        })
        alert('Testing started. Please wait for the results.')
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
    btnShowResult.addEventListener('click', function () {
        const feature = document.getElementById('feature-select-testing').value;
        const classLimit = document.getElementById('class-limit-select-testing').value;
        const camera = document.getElementById('camera-select-testing').value;
        alert('Fetching results. Please wait.')
        fetch('/api/get-test-result', {
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
            .then(response => {
                if (!response.ok) {
                    throw new Error('Result file not found');
                }
                return response.json();
            })
            .then(data => {
                displayResults(data);
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Error fetching results: ' + error.message);
                resultsContent.innerHTML = '<div class="alert alert-danger">Error fetching results. Please try again.</div>';
            });
    });

    btnClearResult.addEventListener('click', function () {
        resultsContainer.style.display = 'none';
        resultsContent.innerHTML = '';
    });

    function displayResults(data) {
        resultsContainer.style.display = 'block';
        let html = `
            <div class="card mb-4">
                <div class="card-body">
                    <h3 class="card-title">Overall Performance</h3>
                    <p class="card-text">Test Accuracy: ${(data.test_accuracy || 0).toFixed(2)}%</p>
                    <p class="card-text">Test Loss: ${(data.test_loss || 0).toFixed(4)}</p>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-body">
                    <h3 class="card-title">Classification Report</h3>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Class</th>
                                <th>Precision</th>
                                <th>Recall</th>
                                <th>F1-Score</th>
                                <th>Support</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        for (let [className, metrics] of Object.entries(data.classification_report || {})) {
            if (className !== 'accuracy' && className !== 'macro avg' && className !== 'weighted avg') {
                html += `
                    <tr>
                        <td>${className}</td>
                        <td>${(metrics.precision || 0).toFixed(3)}</td>
                        <td>${(metrics.recall || 0).toFixed(3)}</td>
                        <td>${(metrics["f1-score"] || 0).toFixed(3)}</td>
                        <td>${metrics.support || 0}</td>
                    </tr>
                `;
            }
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-body">
                    <h3 class="card-title">Macro Average</h3>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Precision</th>
                                <th>Recall</th>
                                <th>F1-Score</th>
                                <th>Support</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>${(data.classification_report["macro avg"].precision || 0).toFixed(3)}</td>
                                <td>${(data.classification_report["macro avg"].recall || 0).toFixed(3)}</td>
                                <td>${(data.classification_report["macro avg"]["f1-score"] || 0).toFixed(3)}</td>
                                <td>${data.classification_report["macro avg"].support || 0}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-body">
                    <h3 class="card-title">Weighted Average</h3>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Precision</th>
                                <th>Recall</th>
                                <th>F1-Score</th>
                                <th>Support</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>${(data.classification_report["weighted avg"].precision || 0).toFixed(3)}</td>
                                <td>${(data.classification_report["weighted avg"].recall || 0).toFixed(3)}</td>
                                <td>${(data.classification_report["weighted avg"]["f1-score"] || 0).toFixed(3)}</td>
                                <td>${data.classification_report["weighted avg"].support || 0}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-body">
                    <h3 class="card-title">Class Metrics</h3>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Class</th>
                                <th>Sensitivity</th>
                                <th>Specificity</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        for (let metric of data.class_metrics || []) {
            html += `
                <tr>
                    <td>${metric.class}</td>
                    <td>${(metric.sensitivity || 0).toFixed(3)}</td>
                    <td>${(metric.specificity || 0).toFixed(3)}</td>
                </tr>
            `;
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="card">
                <div class="card-body">
                    <h3 class="card-title">Confusion Matrix</h3>
                    <table class="table table-bordered">
                        <tbody>
        `;

        for (let row of data.confusion_matrix || []) {
            html += '<tr>';
            for (let cell of row) {
                const cellColor = cell !== 0 ? 'style="background-color:rgb(179, 160, 168);"' : '';
                html += `<td ${cellColor}>${cell}</td>`;
            }
            html += '</tr>';
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        if (data.plot_image_path) {
            html += `
                <div class="card mb-4">
                    <div class="card-body">
                        <h3 class="card-title">Performance Plot</h3>
                        <img src="${data.plot_image_path}" alt="Performance Plot" class="img-fluid">
                    </div>
                </div>
            `;
        }

        resultsContent.innerHTML = html;
    }
});
