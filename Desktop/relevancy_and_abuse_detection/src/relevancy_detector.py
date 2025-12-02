"""
Relevancy Detection Model - Road vs Non-Road Image Classification
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
# Removed pre-trained model import - building custom CNN from scratch
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from tqdm import tqdm
import pickle

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *
from utils.helpers import load_and_preprocess_image, plot_training_history, plot_confusion_matrix

class RelevancyDetector:
    """Road Relevancy Detection Model"""
    
    def __init__(self):
        self.model = None
        self.history = None
        self.class_names = ['irrelevant', 'relevant']
        self.model_path = RELEVANCY_MODEL_PATH
        
    def create_model(self, input_shape=(224, 224, 3)):
        """Create the relevancy detection model - Custom CNN from scratch"""
        print("Creating custom relevancy detection CNN model from scratch...")
        
        # Build custom CNN architecture from scratch
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=input_shape),
            
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.2),
            
            # Second Convolutional Block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.2),
            
            # Third Convolutional Block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),
            
            # Fourth Convolutional Block
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),
            
            # Global pooling and dense layers
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.4),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=LEARNING_RATE),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        print("Custom relevancy detection CNN model created successfully!")
        print(f"Total parameters: {model.count_params():,}")
        return model
    
    def create_data_generators(self, train_dir, val_dir):
        """Create data generators for training"""
        
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Only rescaling for validation
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=True
        )
        
        validation_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=False
        )
        
        return train_generator, validation_generator
    
    def train(self, train_dir=None, val_dir=None, epochs=EPOCHS):
        """Train the relevancy detection model"""
        
        if train_dir is None:
            train_dir = os.path.join(PROCESSED_DATA_DIR, 'train')
        if val_dir is None:
            val_dir = os.path.join(PROCESSED_DATA_DIR, 'val')
        
        print(f"Training relevancy detection model...")
        print(f"Train directory: {train_dir}")
        print(f"Validation directory: {val_dir}")
        
        # Check if directories exist
        if not os.path.exists(train_dir) or not os.path.exists(val_dir):
            print("Training directories not found. Please run data preparation first.")
            return None
        
        # Create model if not exists
        if self.model is None:
            self.create_model()
        
        # Create data generators
        train_generator, val_generator = self.create_data_generators(train_dir, val_dir)
        
        print(f"Found {train_generator.samples} training images")
        print(f"Found {val_generator.samples} validation images")
        print(f"Classes: {train_generator.class_indices}")
        
        # Define callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5,
                min_lr=1e-7
            ),
            keras.callbacks.ModelCheckpoint(
                os.path.join(self.model_path, 'best_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                save_weights_only=False
            )
        ]
        
        # Train the model
        steps_per_epoch = train_generator.samples // BATCH_SIZE
        validation_steps = val_generator.samples // BATCH_SIZE
        
        self.history = self.model.fit(
            train_generator,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            validation_data=val_generator,
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        # Fine-tune the model
        print("\nFine-tuning the model...")
        self._fine_tune_model(train_generator, val_generator, epochs=10)
        
        # Save the model
        self.save_model()
        
        # Plot training history
        plot_training_history(self.history, "Relevancy Detection")
        
        return self.history
    
    def _fine_tune_model(self, train_generator, val_generator, epochs=10):
        """Fine-tune the pre-trained layers"""
        
        # Unfreeze the top layers of the base model
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Fine-tune from this layer onwards
        fine_tune_at = 100
        
        # Freeze all the layers before fine_tune_at
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False
        
        # Use a lower learning rate for fine-tuning
        self.model.compile(
            optimizer=Adam(learning_rate=LEARNING_RATE/10),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Continue training
        fine_tune_epochs = epochs
        total_epochs = len(self.history.history['loss']) + fine_tune_epochs
        
        history_fine = self.model.fit(
            train_generator,
            steps_per_epoch=train_generator.samples // BATCH_SIZE,
            epochs=total_epochs,
            initial_epoch=len(self.history.history['loss']),
            validation_data=val_generator,
            validation_steps=val_generator.samples // BATCH_SIZE,
            verbose=1
        )
        
        # Merge histories
        for key in self.history.history.keys():
            self.history.history[key].extend(history_fine.history[key])
    
    def evaluate(self, test_dir=None):
        """Evaluate the model on test data"""
        
        if test_dir is None:
            test_dir = os.path.join(PROCESSED_DATA_DIR, 'test')
        
        if not os.path.exists(test_dir):
            print("Test directory not found.")
            return None
        
        # Create test data generator
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=False
        )
        
        print(f"Evaluating on {test_generator.samples} test images...")
        
        # Evaluate
        test_loss, test_accuracy = self.model.evaluate(test_generator, verbose=1)
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test Loss: {test_loss:.4f}")
        
        # Get predictions
        predictions = self.model.predict(test_generator, verbose=1)
        predicted_classes = (predictions > 0.5).astype(int).flatten()
        true_classes = test_generator.classes
        
        # Plot confusion matrix
        plot_confusion_matrix(true_classes, predicted_classes, 
                            self.class_names, "Relevancy Detection")
        
        return test_accuracy, test_loss
    
    def predict(self, image_path):
        """Predict if an image is relevant (road-related)"""
        
        if self.model is None:
            self.load_model()
        
        # Preprocess image
        image = load_and_preprocess_image(image_path)
        if image is None:
            return None, 0.0
        
        # Make prediction
        image_batch = np.expand_dims(image, axis=0)
        prediction = self.model.predict(image_batch, verbose=0)
        confidence = float(prediction[0][0])
        
        # Determine class
        if confidence > 0.5:
            predicted_class = 'relevant'
        else:
            predicted_class = 'irrelevant'
            confidence = 1 - confidence
        
        return predicted_class, confidence
    
    def predict_batch(self, image_paths):
        """Predict multiple images"""
        results = []
        
        for image_path in tqdm(image_paths, desc="Predicting"):
            result = self.predict(image_path)
            results.append(result)
        
        return results
    
    def save_model(self):
        """Save the trained model"""
        if self.model is None:
            print("No model to save")
            return
        
        # Save the full model
        model_file = os.path.join(self.model_path, 'relevancy_model.h5')
        self.model.save(model_file)
        
        # Save training history
        history_file = os.path.join(self.model_path, 'training_history.pkl')
        with open(history_file, 'wb') as f:
            pickle.dump(self.history.history if self.history else {}, f)
        
        print(f"Model saved to {model_file}")
    
    def load_model(self):
        """Load a trained model"""
        model_file = os.path.join(self.model_path, 'relevancy_model.h5')
        
        if os.path.exists(model_file):
            self.model = keras.models.load_model(model_file)
            print(f"Model loaded from {model_file}")
            
            # Load training history if available
            history_file = os.path.join(self.model_path, 'training_history.pkl')
            if os.path.exists(history_file):
                with open(history_file, 'rb') as f:
                    history_dict = pickle.load(f)
                    # Create a mock history object
                    class MockHistory:
                        def __init__(self, history_dict):
                            self.history = history_dict
                    self.history = MockHistory(history_dict)
            
            return True
        else:
            print(f"No saved model found at {model_file}")
            return False
    
    def get_model_summary(self):
        """Get model architecture summary"""
        if self.model is None:
            print("No model created yet")
            return None
        
        return self.model.summary()

def main():
    """Main function for training the relevancy detection model"""
    
    print("=== Road Relevancy Detection Model ===\n")
    
    # Create detector
    detector = RelevancyDetector()
    
    # Check if trained model exists
    if detector.load_model():
        print("Loaded existing model.")
        
        # Evaluate if test data exists
        test_dir = os.path.join(PROCESSED_DATA_DIR, 'test')
        if os.path.exists(test_dir):
            detector.evaluate()
    else:
        print("Training new model...")
        
        # Train the model
        history = detector.train()
        
        if history:
            print("Training completed successfully!")
            
            # Evaluate the model
            detector.evaluate()
        else:
            print("Training failed. Please check your data directories.")
    
    # Test prediction on sample images
    sample_dir = os.path.join('data', 'sample')
    if os.path.exists(sample_dir):
        print(f"\nTesting predictions on sample images...")
        
        sample_images = [f for f in os.listdir(sample_dir) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for image_name in sample_images:
            image_path = os.path.join(sample_dir, image_name)
            predicted_class, confidence = detector.predict(image_path)
            print(f"{image_name}: {predicted_class} ({confidence:.2f})")

if __name__ == "__main__":
    main()
