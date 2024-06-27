import pickle
from datetime import datetime
import logging
import os
from typing import Tuple, Union, List

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

MODEL_PATH = os.path.join('challenge', 'models', 'model.pkl')
THRESHOLD_IN_MINUTES = 15

class DelayModel:

    def __init__(
        self
    ):
        self._model = self.__load_model(MODEL_PATH)
        self._features = [
            "OPERA_Latin American Wings", 
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]
    
    def __load_model(self, filename: str):
        if os.path.exists(MODEL_PATH):
            with open(filename, 'rb') as fp:
                return pickle.load(fp)
        else:
            return None
        
    def get_min_diff(self, data):
        fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = ((fecha_o - fecha_i).total_seconds())/60
        return min_diff

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        
        if target_column:
            data['min_diff'] = data.apply(self.get_min_diff, axis=1)
            data['delay'] = np.where(data['min_diff'] > THRESHOLD_IN_MINUTES, 1, 0)
        
        # Generate one-hot encodings
        features = pd.concat([
            pd.get_dummies(data['OPERA'], prefix='OPERA'),
            pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO'),
            pd.get_dummies(data['MES'], prefix='MES')
        ], axis=1)

        # Ensure all expected feature columns are present
        for feature in self._features:
            if feature not in features.columns:
                features[feature] = 0

        # Select the top features
        features = features[self._features]
        
        if target_column:
            target = pd.DataFrame(data[target_column])
            return features, target
        else:
            return features

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """

        x_train, x_test, y_train, y_test = train_test_split(
            features, target, test_size=0.33, random_state=42)
        
        # Calculate the scale for balancing the classes
        n_y0 = int((target == 0).sum())
        n_y1 = int((target == 1).sum())
        scale = n_y0 / n_y1

        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01, scale_pos_weight=scale)
        self._model.fit(x_train, y_train)

        # Log confusion matrix and classification report for training feedback
        y_preds = self._model.predict(x_test)
        logging.info("Confusion Matrix:\n%s", confusion_matrix(y_test, y_preds))
        logging.info("Classification Report:\n%s", classification_report(y_test, y_preds))
        
        # Ensure the directory exists before saving the model
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        # Save the model to a file
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self._model, f)

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """
        predictions = self._model.predict(features)
        return predictions.tolist()
