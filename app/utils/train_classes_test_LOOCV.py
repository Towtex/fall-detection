import warnings
import os
import time
import os.path
import glob
import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Dropout, ZeroPadding3D, GlobalAveragePooling2D
from tensorflow.keras.layers import LSTM
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.layers import TimeDistributed
from tensorflow.keras.layers import (Conv2D, MaxPooling3D, Conv3D, MaxPooling2D)
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping, CSVLogger, Callback
from utils.dataset_new import DatasetNew

#gpu_devices = tf.config.experimental.list_physical_devices("GPU")
#print(gpu_devices)
#for device in gpu_devices:
#    tf.config.experimental.set_memory_growth(device, True)
# gpus = tf.config.list_physical_devices('GPU')
# if gpus:
#   # Restrict TensorFlow to only use the first GPU
#   try:
#     tf.config.set_visible_devices(gpus[0], 'GPU')
#   except RuntimeError as e:
#     # Visible devices must be set before GPUs have been initialized
#     print(e)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

def manage_model_files(model_folder, max_models=3):
    """Keep only the best `max_models` models and delete the rest."""
    model_files = glob.glob(os.path.join(model_folder, '*.hdf5'))
    if len(model_files) <= max_models:
        return

    # Extract validation loss from filenames and sort by it
    model_files.sort(key=lambda x: x.split('-')[2])
    # Keep only the best `max_models` models
    for model_file in model_files[max_models:]:
        print(f"Deleting model file: {model_file} to save space.")
        os.remove(model_file)

class AbortCallback(Callback):
    def __init__(self, abort_signal, model_folder):
        """
        Callback to abort training if the signal is set.
        """
        super().__init__()
        self.abort_signal = abort_signal
        self.model_folder = model_folder

    def on_epoch_end(self, epoch, logs=None):
        if self.abort_signal.is_set():
            print(f"Training aborted at epoch {epoch + 1}.")
            self.model.stop_training = True
        # Manage model files after each epoch
        manage_model_files(self.model_folder)

def train(feature_str: str, class_limit: str, subject: str, camera: str, abort_signal):
    seq_length = 18
    batch_size = 100
    epochs = 1000
    
    output_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'output',
        )
    )
    os.makedirs(output_folder, exist_ok=True)
    
    model_folder = os.path.join(
        output_folder,
        f'Subject_{subject}',
        f'train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_LOOCV_{feature_str}',
        'weight_models'
    )
    os.makedirs(model_folder, exist_ok=True)
    
    all_model_files = glob.glob(os.path.join(model_folder, '*.hdf5'))
    all_model_files.sort(key=os.path.getctime, reverse=True)   
    if len(all_model_files) != 0:
        saved_model = all_model_files[0] 
    else:
        saved_model = None
    print(f"Load model: {saved_model}")
    
    data_file = os.path.join(
        output_folder,
        f'Subject_{subject}',
        f'train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_LOOCV_{feature_str}.csv'
    )
    
    checkpointer = ModelCheckpoint(
        filepath = os.path.join(
            model_folder,
            'lstm_features-val_loss_{val_loss:.3f}-epoch_{epoch:03d}.hdf5'
        ),
        verbose = 1,
        save_best_only = True,
        monitor='val_loss'
    )

    tb = TensorBoard(log_dir=os.path.join(output_folder, 'logs', 'lstm'))
    early_stopping = EarlyStopping(
        monitor = 'val_loss',
        patience = 10,
        verbose = 1
    )

    timestamp = time.time()
    log_dir = os.path.join(
        output_folder,
        f'Subject_{subject}',
        f'train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_LOOCV_{feature_str}',
        'logs'
    )
    os.makedirs(log_dir, exist_ok=True)
    csv_logger = CSVLogger(
        os.path.join(
            log_dir, 
            f'lstm-training-{timestamp}.log'
        )
    )
    abort_callback = AbortCallback(abort_signal, model_folder)
    dataset = DatasetNew(data_file=data_file)

    train_x, train_y = dataset.get_all_feature_sequences('train')
    test_x, test_y = dataset.get_all_feature_sequences('test')
    
    features_length = 4096 if camera == '1_2' else 2048
    if saved_model is not None:
        print(f"Loading previous model: {saved_model}")
        classification_model = tf.keras.models.load_model(saved_model)
    else:  
        print("Creating new model.")
        classification_model = Sequential([
            LSTM(1024, return_sequences=False, input_shape=(seq_length, features_length), dropout=0.5),
            Dense(512, activation='relu'),
            Dropout(0.5),
            Dense(class_limit, activation='softmax')
        ])
        optimizer = Adam(learning_rate=1e-5)
        classification_model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
        
    print(f"train_x shape: {train_x.shape}, train_y shape: {train_y.shape}")
    
    start_time = time.time()
    classification_model.fit(
        train_x,
        train_y,
        batch_size=batch_size,
        validation_data=(test_x, test_y),
        verbose=1,
        callbacks=[tb, early_stopping, csv_logger, checkpointer, abort_callback],
        epochs=epochs
    )
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Training completed in {execution_time:.2f} seconds.")
    return f'Training completed in {execution_time:.2f} seconds.'

