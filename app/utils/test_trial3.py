import pprint
import warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from utils.dataset_new import DatasetNew
import keras.models
import glob
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix
import json

warnings.filterwarnings('ignore')

def get_display_labels(class_limit):
    # Return display labels based on class limit
    if class_limit == 2:
        return ['Falling', 'NotFalling']
    elif class_limit == 7:
        return ['Falling', 'Walking', 'Standing', 'Sitting', 'Picking', 'Jumping', 'Laying']
    else:
        return ['Falling forward(hands)', 'Falling forward(knees)', 'Falling backward', 'Falling sideward', 
                'Falling when sitting', 'Walking', 'Standing', 'Sitting', 'Picking', 'Jumping', 'Laying']

def load_model_and_data(main_folder, class_limit, camera, feature):
    # Load the model and data
    model_str = os.path.join(
        main_folder,
        f'train_data_{class_limit}_classes_cam_{camera}_test_trial3_{feature}'
    )
    model_folder = os.path.join(model_str, 'weight_models')
    all_model_files = glob.glob(os.path.join(model_folder, '*.hdf5'))
    all_model_files.sort(key=os.path.getctime, reverse=True)
    for file_name in all_model_files:
        if file_name != all_model_files[0]:
            os.remove(file_name)
    saved_model = all_model_files[0] if all_model_files else None
    print(f'Load model: {saved_model}')
    
    data_file = os.path.join(
        main_folder,
        f'train_data_{class_limit}_classes_cam_{camera}_test_trial3_{feature}.csv'
    )
    model = keras.models.load_model(saved_model)
    data_set = DatasetNew(data_file=data_file)
    x_test, y_test = data_set.get_all_feature_sequences('test')
    
    # Print shapes for debugging
    print(f'Model input shape: {model.input_shape[1:]}')
    print(f'Test data shape: {x_test.shape[1:]}')
    
    # Ensure the input shape of the model matches the shape of the test data
    if model.input_shape[1:] != x_test.shape[1:]:
        raise ValueError(f'Expected input shape {model.input_shape[1:]}, but got {x_test.shape[1:]}')
    
    return model, x_test, y_test, model_str

def evaluate_model(model, x_test, y_test, file_writer):
    # Evaluate the model
    score = model.evaluate(x_test, y_test, verbose=0)
    file_writer.write(f'Test loss: {score[0]}\n')
    file_writer.write(f'Test accuracy: {score[1] * 100}\n')
    file_writer.write('-------------------------------------------------\n')
    return score

def generate_confusion_matrix(model, x_test, y_test, class_limit, display_labels, file_writer):
    # Generate confusion matrix and classification report
    predicted_classes = np.argmax(model.predict(x_test), axis=-1)
    actual_classes = np.asarray([val.tolist().index(1) for val in y_test])
    conf_mat = tf.math.confusion_matrix(labels=actual_classes, predictions=predicted_classes, num_classes=class_limit)
    confusion_matrix = metrics.confusion_matrix(actual_classes, predicted_classes)
    cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix=confusion_matrix, display_labels=display_labels)
    accuracy = metrics.accuracy_score(actual_classes, predicted_classes)
    print(f'Accuracy = {accuracy * 100}%')
    print(f'Confusion Matrix:\n{conf_mat}')
    
    file_writer.write(f'Confusion Matrix:\n{conf_mat}\n')
    file_writer.write('-------------------------------------------------\n')
    report = classification_report(actual_classes, predicted_classes)
    print(report)
    file_writer.write(f'{report}\n')
    file_writer.write('-------------------------------------------------\n')
    return conf_mat, cm_display, report, actual_classes, predicted_classes

def calculate_class_metrics(conf_mat, n_classes, file_writer):
    # Calculate class metrics
    results = {'class_metrics': []}
    for i in range(n_classes):
        tp = conf_mat[i, i]
        fn = sum(conf_mat[i, :]) - tp
        fp = sum(conf_mat[:, i]) - tp
        tn = sum(sum(conf_mat)) - tp - fn - fp
        
        sensitivity = tp / (tp + fn)
        specificity = tn / (tn + fp)
        
        print(f'Class {i}: Sensitivity = {sensitivity:.2f}, Specificity = {specificity:.2f}')
        file_writer.write(f'Class {i}: Sensitivity = {sensitivity:.2f}, Specificity = {specificity:.2f}\n')
        
        results['class_metrics'].append({
            'class': i,
            'sensitivity': sensitivity,
            'specificity': specificity
        })
    return results

def save_results_to_json(results, output_path):
    # Convert 'class_metrics' EagerTensors to floats
    for metric in results['class_metrics']:
        for key, value in metric.items():
            if isinstance(value, tf.Tensor):
                metric[key] = value.numpy()  # Convert EagerTensor to float
    
    # Convert 'classification_report' if necessary
    if isinstance(results.get('classification_report'), dict):
        results['classification_report'] = {
            k: (v.tolist() if isinstance(v, np.ndarray) else v)
            for k, v in results['classification_report'].items()
        }
    
    # Convert 'confusion_matrix' to list if needed
    if isinstance(results['confusion_matrix'], tf.Tensor):
        results['confusion_matrix'] = results['confusion_matrix'].numpy().tolist()
    elif isinstance(results['confusion_matrix'], np.ndarray):
        results['confusion_matrix'] = results['confusion_matrix'].tolist()

    # Ensure 'test_accuracy' and 'test_loss' are floats
    if isinstance(results['test_accuracy'], tf.Tensor):
        results['test_accuracy'] = results['test_accuracy'].numpy()
    if isinstance(results['test_loss'], tf.Tensor):
        results['test_loss'] = results['test_loss'].numpy()
    
    # Write results to JSON
    with open(output_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)
        print(f"Saved results to JSON successfully!")

def save_results(results, model_str, cm_display, class_limit):
    # Save results and plot confusion matrix
    if class_limit == 2:
        cm_display.plot(xticks_rotation='horizontal', colorbar=False)
    else:
        fig, ax = plt.subplots(figsize=(15, 16))
        cm_display.plot(ax=ax, xticks_rotation='vertical', colorbar=False)
    
    cm_display.figure_.savefig(f'{model_str}_performance_eval.png')
    plt.show()

def test(feature: str, class_limit: int, camera: str):
    # Main test function
    main_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            'output'
        )
    )
    
    model, x_test, y_test, model_str = load_model_and_data(main_folder, class_limit, camera, feature)
    log_file = f'{model_str}_performance_eval.txt'
    file_writer = open(log_file, 'w')
    print("Starting evaluation...")
    display_labels = get_display_labels(class_limit)
    score = evaluate_model(model, x_test, y_test, file_writer)
    conf_mat, cm_display, report, actual_classes, predicted_classes = generate_confusion_matrix(
        model, x_test, y_test, class_limit, display_labels, file_writer)
    
    results = {
        'test_loss': score[0],
        'test_accuracy': score[1] * 100,
        'confusion_matrix': conf_mat.numpy().tolist(),
        'classification_report': classification_report(actual_classes, predicted_classes, output_dict=True)
    }
    class_metrics = calculate_class_metrics(conf_mat, conf_mat.shape[0], file_writer)
    results.update(class_metrics)
    
    save_results(results, model_str, cm_display, class_limit)
    file_writer.close()
    
    # Save results to JSON file
    save_results_to_json(results, f'{model_str}_performance_eval.json')
