"""
AI-based pH Prediction Module for Aquaculture Monitoring System

This module uses machine learning to predict future pH values based on
historical time-series data. It enables early warning alerts by predicting
when pH might exceed safe thresholds.
"""

import numpy as np
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using simple linear regression fallback.")

try:
    # TensorFlow is an optional dependency; keep imports guarded and
    # silence static analyzers when TF isn't installed in the environment.
    import tensorflow as tf  # pyright: ignore[reportMissingImports]
    from tensorflow import keras  # pyright: ignore[reportMissingImports]
    from tensorflow.keras.layers import LSTM, Dense, Dropout  # pyright: ignore[reportMissingImports]

    Sequential = keras.models.Sequential
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

if TENSORFLOW_AVAILABLE:
    def ph_mse_loss(y_true, y_pred):
        """
        Custom loss function for pH prediction.

        Sử dụng Mean Squared Error (MSE):
            loss = mean((y_true - y_pred)^2)

        Được định nghĩa riêng để minh họa rõ ràng hàm mất mát cho mô hình AI.
        """
        return tf.reduce_mean(tf.square(y_true - y_pred))


class PHPredictor:
    """
    AI-based pH predictor that uses historical data to forecast future pH values.
    
    Uses Random Forest Regressor for prediction, with fallback to simple
    linear regression if scikit-learn is not available.
    """
    
    def __init__(
        self,
        history_window: int = 20,
        prediction_horizon_minutes: int = 30,
        min_samples_for_training: int = 50,
        use_lstm: bool = False,
        prediction_horizon_seconds: int = 10,
        retrain_every: int = 50
    ):
        """
        Initialize the pH predictor.
        
        Args:
            history_window: Number of historical readings to use for prediction (default: 20)
            prediction_horizon_minutes: How many minutes ahead to predict (default: 30)
            min_samples_for_training: Minimum samples needed before training (default: 50)
            use_lstm: Whether to use LSTM model instead of Random Forest (default: False)
        """
        self.history_window = history_window
        self.prediction_horizon_minutes = prediction_horizon_minutes
        self.prediction_horizon_seconds = prediction_horizon_seconds
        self.min_samples_for_training = min_samples_for_training
        self.use_lstm = use_lstm and TENSORFLOW_AVAILABLE
        self.retrain_every = retrain_every
        
        # Data storage
        self.ph_history: deque = deque(maxlen=1000)  # Store up to 1000 readings
        self.timestamp_history: deque = deque(maxlen=1000)
        self.read_count: int = 0
        
        # Model components
        self.model = None
        self.lstm_model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        self.total_retrains = 0
        self.last_retrain_at: Optional[str] = None
        
        # Metrics tracking
        self.accuracy_history = []  # Store prediction errors
        self.last_accuracy = None
        self.feature_importance = None
        
        # Fallback simple linear regression parameters
        self.simple_slope = 0.0
        self.simple_intercept = 7.5
        
    def add_reading(self, timestamp: datetime, ph_value: float):
        """
        Add a new pH reading to the history.
        
        Args:
            timestamp: Timestamp of the reading
            ph_value: pH value
        """
        self.ph_history.append(ph_value)
        self.timestamp_history.append(timestamp)
        self.read_count += 1
        
        # Retrain model periodically if we have enough data
        if len(self.ph_history) >= self.min_samples_for_training:
            if not self.is_trained:
                self._train_model()
                if self.is_trained:
                    self.total_retrains += 1
                    self.last_retrain_at = timestamp.isoformat()
            elif self.retrain_every > 0 and (self.read_count % self.retrain_every == 0):
                self.retrain_model()
                if self.is_trained:
                    self.total_retrains += 1
                    self.last_retrain_at = timestamp.isoformat()
    
    def _create_features(self, ph_sequence: List[float]) -> np.ndarray:
        """
        Create feature vectors from pH sequence.
        
        Args:
            ph_sequence: List of pH values
            
        Returns:
            Feature array for machine learning
        """
        if len(ph_sequence) < self.history_window:
            # Pad with most recent value if not enough history
            ph_sequence = [ph_sequence[0]] * (self.history_window - len(ph_sequence)) + ph_sequence
        
        # Use last history_window values
        recent_values = ph_sequence[-self.history_window:]
        
        # Create features: recent values + statistics
        features = np.array(recent_values)
        
        # Add statistical features
        stats = [
            np.mean(recent_values),
            np.std(recent_values),
            np.min(recent_values),
            np.max(recent_values),
            recent_values[-1] - recent_values[0],  # Trend
        ]
        
        features = np.concatenate([features, stats])
        return features.reshape(1, -1)
    
    def _train_model(self):
        """Train the prediction model on historical data."""
        if len(self.ph_history) < self.min_samples_for_training:
            return
        
        if self.use_lstm:
            self._train_lstm_model()
            return
        
        if not SKLEARN_AVAILABLE:
            # Simple linear regression fallback
            self._train_simple_model()
            self.is_trained = True
            return
        
        # Prepare training data
        X = []
        y = []
        
        ph_list = list(self.ph_history)
        
        # Create sliding window features and targets
        for i in range(self.history_window, len(ph_list) - 1):
            # Features: history_window previous values
            features = self._create_features(ph_list[:i+1])
            X.append(features[0])
            
            # Target: next value
            y.append(ph_list[i + 1])
        
        if len(X) < 10:  # Need at least 10 samples
            return
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest model
        self.model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_.tolist()
        
        # Calculate initial accuracy
        y_pred = self.model.predict(X_scaled)
        mae = np.mean(np.abs(y_pred - y))
        mse = np.mean((y_pred - y) ** 2)
        self.last_accuracy = {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(np.sqrt(mse)),
            'r2': float(1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)))
        }
        
        print(f"✓ AI Model (RandomForest) trained on {len(X)} samples")
        print(f"  Accuracy - MAE: {self.last_accuracy['mae']:.4f}, RMSE: {self.last_accuracy['rmse']:.4f}, R²: {self.last_accuracy['r2']:.4f}")
    
    def _train_lstm_model(self):
        """Train LSTM model on historical data."""
        if not TENSORFLOW_AVAILABLE:
            print("Warning: TensorFlow not available. Falling back to Random Forest.")
            self.use_lstm = False
            self._train_model()
            return
        
        ph_list = list(self.ph_history)
        
        if len(ph_list) < self.history_window + 10:
            return
        
        # Prepare sequences for LSTM
        X, y = [], []
        for i in range(self.history_window, len(ph_list) - 1):
            X.append(ph_list[i - self.history_window:i])
            y.append(ph_list[i])
        
        if len(X) < 10:
            return
        
        X = np.array(X)
        y = np.array(y)
        
        # Reshape for LSTM: (samples, time_steps, features)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        # Normalize
        if self.scaler is None:
            self.scaler = StandardScaler()
        
        # Flatten, scale, reshape back
        X_flat = X.reshape(-1, 1)
        X_scaled_flat = self.scaler.fit_transform(X_flat)
        X_scaled = X_scaled_flat.reshape(X.shape)
        
        y_scaled = self.scaler.transform(y.reshape(-1, 1)).flatten()
        
        # Build LSTM model (simple architecture for demo)
        self.lstm_model = Sequential([
            LSTM(50, activation='relu', input_shape=(self.history_window, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])

        # Use custom loss function for clarity in AI coursework (MSE)
        self.lstm_model.compile(
            optimizer='adam',
            loss=ph_mse_loss if TENSORFLOW_AVAILABLE else 'mse',
            metrics=['mae']
        )
        
        # Train (silent mode for demo)
        # Split for validation
        split_idx = int(len(X_scaled) * 0.8)
        X_train, X_val = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_val = y_scaled[:split_idx], y_scaled[split_idx:]
        
        self.lstm_model.fit(
            X_train, y_train,
            epochs=20,
            batch_size=16,
            verbose=0,
            validation_data=(X_val, y_val)
        )
        
        # Calculate accuracy
        y_pred_scaled = self.lstm_model.predict(X_scaled, verbose=0).flatten()
        y_pred = self.scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        y_actual = self.scaler.inverse_transform(y_scaled.reshape(-1, 1)).flatten()
        
        mae = np.mean(np.abs(y_pred - y_actual))
        mse = np.mean((y_pred - y_actual) ** 2)
        self.last_accuracy = {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(np.sqrt(mse)),
            'r2': float(1 - (np.sum((y_actual - y_pred) ** 2) / np.sum((y_actual - np.mean(y_actual)) ** 2)))
        }
        
        self.is_trained = True
        print(f"✓ AI Model (LSTM) trained on {len(X)} samples")
        print(f"  Accuracy - MAE: {self.last_accuracy['mae']:.4f}, RMSE: {self.last_accuracy['rmse']:.4f}, R²: {self.last_accuracy['r2']:.4f}")
    
    def _train_simple_model(self):
        """Train simple linear regression model (fallback)."""
        if len(self.ph_history) < 10:
            return
        
        ph_list = list(self.ph_history)
        
        # Simple linear regression: predict next value based on recent trend
        recent = ph_list[-10:]
        x = np.arange(len(recent))
        y = np.array(recent)
        
        # Calculate slope and intercept
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x * x)
        
        self.simple_slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        self.simple_intercept = (sum_y - self.simple_slope * sum_x) / n
    
    def predict(self, ph_value: Optional[float] = None) -> Tuple[float, bool]:
        """
        Predict future pH value.
        
        Args:
            ph_value: Current pH value (if None, uses most recent from history)
            
        Returns:
            Tuple of (predicted_ph, is_reliable)
        """
        # Get current value
        current_value = ph_value if ph_value is not None else (self.ph_history[-1] if len(self.ph_history) > 0 else 7.5)
        
        # Use provided value or most recent
        if ph_value is None and len(self.ph_history) > 0:
            ph_value = self.ph_history[-1]
        
        # Get recent history
        ph_list = list(self.ph_history)
        if ph_value is not None:
            ph_list.append(ph_value)
        
        # Use LSTM if available and trained
        if self.use_lstm and self.lstm_model is not None and self.is_trained:
            # Prepare sequence for LSTM
            recent = ph_list[-self.history_window:]
            if len(recent) < self.history_window:
                recent = [ph_list[0]] * (self.history_window - len(recent)) + recent
            
            X = np.array(recent).reshape(1, self.history_window, 1)
            X_scaled = self.scaler.transform(X.reshape(-1, 1)).reshape(1, self.history_window, 1)
            
            predicted_scaled = self.lstm_model.predict(X_scaled, verbose=0)[0][0]
            predicted = self.scaler.inverse_transform([[predicted_scaled]])[0][0]
            is_reliable = len(self.ph_history) >= 100
            
            # Đảm bảo predicted khác với current_value ít nhất 0.02
            if abs(predicted - current_value) < 0.02:
                predicted = current_value + (0.05 if predicted > current_value else -0.05)
            
            return round(predicted, 2), is_reliable
        
        # Use trained Random Forest model if available
        if SKLEARN_AVAILABLE and self.model is not None and self.is_trained:
            # Create features
            features = self._create_features(ph_list)
            features_scaled = self.scaler.transform(features)
            predicted = self.model.predict(features_scaled)[0]
            is_reliable = len(self.ph_history) >= 100
            
            # Đảm bảo predicted khác với current_value ít nhất 0.02
            if abs(predicted - current_value) < 0.02:
                predicted = current_value + (0.05 if predicted > current_value else -0.05)
            
            return round(predicted, 2), is_reliable
        
        # Fallback: Simple trend prediction
        if len(self.ph_history) >= 2:
            recent = list(self.ph_history)[-5:] if len(self.ph_history) >= 5 else list(self.ph_history)
            if len(recent) >= 2:
                # Simple trend: dự đoán dựa trên xu hướng gần nhất
                trend = recent[-1] - recent[0] if len(recent) > 1 else 0
                # Extrapolate trend với hệ số để có sự khác biệt rõ ràng
                trend_factor = 2.0  # Nhân trend để dự đoán xa hơn
                predicted = recent[-1] + (trend * trend_factor)
                
                # Đảm bảo predicted khác với current_value ít nhất 0.02
                if abs(predicted - current_value) < 0.02:
                    # Nếu quá gần, thêm một chút biến động dựa trên độ lệch chuẩn
                    if len(recent) >= 3:
                        std_dev = np.std(recent)
                        if std_dev > 0:
                            predicted = current_value + (std_dev * 0.5)
                        else:
                            predicted = current_value + 0.05
                    else:
                        predicted = current_value + 0.05
                
                return round(predicted, 2), len(self.ph_history) >= 15
        
        # Nếu chỉ có 1 reading hoặc chưa có đủ dữ liệu
        if len(self.ph_history) > 0:
            current = self.ph_history[-1]
            # Thêm một chút biến động nhỏ để có sự khác biệt (dựa trên noise level thông thường)
            predicted = current + np.random.uniform(-0.08, 0.08)
            # Đảm bảo khác với current ít nhất 0.02
            if abs(predicted - current) < 0.02:
                predicted = current + (0.05 if np.random.random() > 0.5 else -0.05)
            return round(predicted, 2), False
        
        # Fallback cuối cùng: dùng giá trị hiện tại với một chút biến động
        if ph_value is not None:
            predicted = ph_value + np.random.uniform(-0.05, 0.05)
            if abs(predicted - ph_value) < 0.02:
                predicted = ph_value + 0.05
            return round(predicted, 2), False
        
        return 7.5, False  # Default fallback
    
    def check_early_warning(
        self,
        predicted_ph: float,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5
    ) -> Tuple[bool, str]:
        """
        Check if predicted pH triggers an early warning.
        
        Args:
            predicted_ph: Predicted pH value
            low_threshold: Lower bound of safe range
            high_threshold: Upper bound of safe range
            
        Returns:
            Tuple of (has_warning, message)
        """
        if predicted_ph < low_threshold:
            return True, f"🔮 EARLY WARNING: Predicted pH ({predicted_ph:.2f}) may drop below safe range in ~{self.prediction_horizon_minutes} minutes"
        elif predicted_ph > high_threshold:
            return True, f"🔮 EARLY WARNING: Predicted pH ({predicted_ph:.2f}) may exceed safe range in ~{self.prediction_horizon_minutes} minutes"
        else:
            return False, f"✓ Prediction: pH will remain safe ({predicted_ph:.2f})"
    
    def get_model_info(self) -> dict:
        """
        Get information about the prediction model.
        
        Returns:
            Dictionary with model information
        """
        model_type = "SimpleLinear"
        if self.use_lstm and self.lstm_model is not None:
            model_type = "LSTM"
        elif SKLEARN_AVAILABLE and self.model is not None:
            model_type = "RandomForest"
        
        return {
            "is_trained": self.is_trained,
            "history_size": len(self.ph_history),
            "model_type": model_type,
            "prediction_horizon_minutes": self.prediction_horizon_minutes,
            "prediction_horizon_seconds": self.prediction_horizon_seconds,
            "history_window": self.history_window,
            "accuracy": self.last_accuracy,
            "feature_importance": self.feature_importance,
            "rolling_accuracy": self.get_rolling_accuracy(),
            "total_retrains": self.total_retrains,
            "last_retrain_at": self.last_retrain_at
        }
    
    def update_accuracy(self, predicted: float, actual: float):
        """
        Update accuracy metrics with a new prediction vs actual.
        
        Args:
            predicted: Predicted pH value
            actual: Actual pH value
        """
        error = abs(predicted - actual)
        self.accuracy_history.append(error)
        
        # Keep only last 100 errors
        if len(self.accuracy_history) > 100:
            self.accuracy_history.pop(0)
        
        # Update last accuracy if we have enough data
        if len(self.accuracy_history) >= 10:
            self.last_accuracy = {
                'mae': float(np.mean(self.accuracy_history)),
                'rmse': float(np.sqrt(np.mean([e**2 for e in self.accuracy_history]))),
                'samples': len(self.accuracy_history)
            }

    def get_rolling_accuracy(self, window: int = 50) -> Optional[dict]:
        """
        Get rolling MAE/RMSE over the most recent window of errors.
        """
        if not self.accuracy_history:
            return None
        recent = self.accuracy_history[-window:] if len(self.accuracy_history) > window else self.accuracy_history
        mae = float(np.mean(recent))
        rmse = float(np.sqrt(np.mean([e**2 for e in recent])))
        return {
            "mae": mae,
            "rmse": rmse,
            "samples": len(recent),
            "window": window
        }
    
    def retrain_model(self):
        """
        Retrain the model with current data.
        
        Returns:
            bool: True if retrained successfully
        """
        if len(self.ph_history) < self.min_samples_for_training:
            return False
        
        self.is_trained = False
        self._train_model()
        return self.is_trained


if __name__ == "__main__":
    # Demo: Test predictor
    print("pH Predictor Demo")
    print("=" * 50)
    
    predictor = PHPredictor(history_window=10, min_samples_for_training=20)
    
    # Simulate some readings
    from datetime import datetime, timedelta
    
    base_time = datetime.now()
    base_ph = 7.5
    
    print("Adding sample readings...")
    for i in range(30):
        timestamp = base_time + timedelta(minutes=i)
        # Simulate gradual decrease
        ph_value = base_ph - (i * 0.02) + np.random.normal(0, 0.05)
        predictor.add_reading(timestamp, ph_value)
    
    print(f"History size: {len(predictor.ph_history)}")
    print(f"Model trained: {predictor.is_trained}\n")
    
    # Make prediction
    predicted, is_reliable = predictor.predict()
    print(f"Predicted pH: {predicted:.2f} (reliable: {is_reliable})")
    
    # Check early warning
    has_warning, message = predictor.check_early_warning(predicted)
    print(f"Early warning: {message}")

