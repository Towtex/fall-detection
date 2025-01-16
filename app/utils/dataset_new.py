import csv
import numpy as np
import glob
import os.path
import operator
from tensorflow.keras.utils import to_categorical

class DatasetNew():
    def __init__(self, data_file):
        self.data_file = data_file
        self.data_list = self.get_data_list()
        self.classes = self.get_classes_name()

    def get_data_list(self):
        try:
            with open(self.data_file, 'r') as fin:    
                reader = csv.reader(fin)
                data = list(reader)
            return data
        except FileNotFoundError:
            print(f"Error: File {self.data_file} not found.")
            return []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []

    def get_classes_name(self):
        print('Length of data = ', len(self.data_list))
        classes = []
        try:
            for item in self.data_list:
                if item[1] not in classes:
                    classes.append(item[1])
            classes = sorted(classes)
            print('Length of classes = ', len(classes))
            return classes
        except IndexError:
            print("Error: Data list is not in the expected format.")
            return []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []

    def get_class_number(self, class_str):
        try:
            label_encoded = self.classes.index(class_str)
            label_hot = to_categorical(label_encoded, len(self.classes))
            assert len(label_hot) == len(self.classes)
            return label_hot
        except ValueError:
            print(f"Error: Class {class_str} not found in classes list.")
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def split_train_test(self):
        train = []
        test = []
        try:
            for item in self.data_list:
                if item[0] == 'train':
                    train.append(item)
                else:
                    test.append(item)
            return train, test
        except IndexError:
            print("Error: Data list is not in the expected format.")
            return [], []
        except Exception as e:
            print(f"Error: {str(e)}")
            return [], []

    def get_all_feature_sequences(self, train_test):
        train, test = self.split_train_test()
        data = train if train_test == 'train' else test
        x, y = [], []
        try:
            for row in data:
                seq_file_path = row[6]
                if os.path.isfile(seq_file_path):
                    x_data = np.load(seq_file_path)
                    sequence = np.asarray(x_data).astype('float32')
                    x.append(sequence)
                    y.append(self.get_class_number(row[1]))
                else:
                    print(f"Error: Sequence file {seq_file_path} not found. Current directory: {os.getcwd()}")
                    print(f"Absolute path check: {os.path.abspath(seq_file_path)}")
                    print(f"Directory contents: {os.listdir(os.path.dirname(seq_file_path))}")
            return np.array(x), np.array(y)
        except IndexError:
            print("Error: Data list is not in the expected format.")
            return np.array([]), np.array([])
        except Exception as e:
            print(f"Error: {str(e)}")
            return np.array([]), np.array([])

    @staticmethod
    def get_frames_path(sample):
        try:
            sub_str = sample[2]
            cam_str = sample[3]
            trial_str = sample[4]
            act_str = sample[5]
            feat_fld = sample[6]
            img_str = sample[7]
            path = os.path.join(
                feat_fld,
                sub_str,
                cam_str,
                trial_str,
                f'{sub_str}{act_str}{trial_str}{cam_str}',
                img_str
            )
            frames_path = sorted(glob.glob(os.path.join(path, '*png')))
            frames_len = int(sample[8])
            return frames_path, frames_len
        except IndexError:
            print("Error: Sample data is not in the expected format.")
            return [], 0
        except Exception as e:
            print(f"Error: {str(e)}")
            return [], 0

    def get_predicted_class_probability(self, predictions, nb_to_return=5):
        try:
            label_predictions = {label: predictions[i] for i, label in enumerate(self.classes)}
            sorted_lps = sorted(label_predictions.items(), key=operator.itemgetter(1), reverse=True)
            result = []
            for i, class_prediction in enumerate(sorted_lps):
                if i > nb_to_return - 1 or class_prediction[1] == 0.0:
                    break
                print(f"{class_prediction[0]}: {class_prediction[1]:.2f}")
                result.append(f"{class_prediction[0]}: {class_prediction[1]:.2f}")
            return result
        except IndexError:
            print("Error: Predictions list is not in the expected format.")
            return []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []
