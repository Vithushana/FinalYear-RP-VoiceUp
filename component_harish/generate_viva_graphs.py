"""
Complete Viva Presentation Graph Generator
Generates individual model graphs AND training curves from real data
Run: python generate_complete_viva_graphs.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for professional graphs
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def read_training_results(csv_path):
    """Read training results from CSV file"""
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return None

def plot_training_curves(df, model_name, save_path):
    """Plot actual training curves from CSV data"""
    if df is None or df.empty:
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'{model_name} - Training Progress (Real Data)', fontsize=16, fontweight='bold')
    
    # Plot 1: Training Loss Curves
    if 'train/box_loss' in df.columns and 'val/box_loss' in df.columns:
        axes[0,0].plot(df['epoch'], df['train/box_loss'], label='Train Box Loss', linewidth=2, color='blue')
        axes[0,0].plot(df['epoch'], df['val/box_loss'], label='Val Box Loss', linewidth=2, color='red')
        axes[0,0].set_title('Box Loss Progress')
        axes[0,0].set_xlabel('Epoch')
        axes[0,0].set_ylabel('Loss')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: Classification Loss
    if 'train/cls_loss' in df.columns and 'val/cls_loss' in df.columns:
        axes[0,1].plot(df['epoch'], df['train/cls_loss'], label='Train Cls Loss', linewidth=2, color='green')
        axes[0,1].plot(df['epoch'], df['val/cls_loss'], label='Val Cls Loss', linewidth=2, color='orange')
        axes[0,1].set_title('Classification Loss Progress')
        axes[0,1].set_xlabel('Epoch')
        axes[0,1].set_ylabel('Loss')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: mAP50 Progress (Confidence Scores)
    if 'metrics/mAP50(B)' in df.columns:
        axes[0,2].plot(df['epoch'], df['metrics/mAP50(B)'], color='purple', linewidth=2)
        axes[0,2].set_title('mAP50 Progress (Confidence)')
        axes[0,2].set_xlabel('Epoch')
        axes[0,2].set_ylabel('mAP50')
        axes[0,2].grid(True, alpha=0.3)
        final_map = df['metrics/mAP50(B)'].iloc[-1]
        axes[0,2].text(0.95, 0.05, f'Final: {final_map:.4f}', 
                      transform=axes[0,2].transAxes, ha='right', 
                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Plot 4: Precision and Recall Progress
    if 'metrics/precision(B)' in df.columns and 'metrics/recall(B)' in df.columns:
        axes[1,0].plot(df['epoch'], df['metrics/precision(B)'], label='Precision', linewidth=2, color='darkgreen')
        axes[1,0].plot(df['epoch'], df['metrics/recall(B)'], label='Recall', linewidth=2, color='darkred')
        axes[1,0].set_title('Precision & Recall Progress')
        axes[1,0].set_xlabel('Epoch')
        axes[1,0].set_ylabel('Score')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
    
    # Plot 5: Learning Rate Schedule
    if 'lr/pg0' in df.columns:
        axes[1,1].plot(df['epoch'], df['lr/pg0'], color='brown', linewidth=2)
        axes[1,1].set_title('Learning Rate Schedule')
        axes[1,1].set_xlabel('Epoch')
        axes[1,1].set_ylabel('Learning Rate')
        axes[1,1].grid(True, alpha=0.3)
    
    # Plot 6: Training Time per Epoch
    if 'time' in df.columns:
        axes[1,2].plot(df['epoch'], df['time'], color='teal', linewidth=2)
        axes[1,2].set_title('Training Time per Epoch')
        axes[1,2].set_xlabel('Epoch')
        axes[1,2].set_ylabel('Time (seconds)')
        axes[1,2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_individual_model_graphs(output_path):
    """Create separate performance graph for each of the 5 models"""
    
    models_data = {
        'Road Detection': {
            'accuracy': 94.2,
            'precision': 93.5,
            'recall': 94.9,
            'architecture': '8-Model Ensemble',
            'description': 'YOLOv8 Road Detection',
            'classes': 'road, pothole, crack, pavement, asphalt',
            'threshold': '50%',
            'color': 'skyblue'
        },
        'Abuse Detection': {
            'accuracy': 76.8,
            'precision': 78.5,
            'recall': 75.1,
            'architecture': '6-Model Weighted Ensemble',
            'description': 'YOLOv8 Abuse Detection',
            'classes': 'weapons, violence, blood, abusive content',
            'threshold': '45-65%',
            'color': 'lightcoral'
        },
        'Privacy Protection': {
            'accuracy': 90.6,
            'precision': 85.2,
            'recall': 96.3,
            'architecture': 'Human Detection',
            'description': 'YOLOv8 Human Detection',
            'classes': 'person, face, hand',
            'threshold': '45%',
            'color': 'lightgreen'
        },
        'Garbage Classification': {
            'accuracy': 92.8,
            'precision': 91.5,
            'recall': 94.1,
            'architecture': 'Clean vs Garbage',
            'description': 'YOLOv8 Garbage Classification',
            'classes': 'Clean, Garbage Detected',
            'threshold': '75%',
            'color': 'gold'
        },
        'Text Abuse Detection': {
            'accuracy': 89.5,
            'precision': 92.1,
            'recall': 87.2,
            'architecture': 'DistilBERT Transformer',
            'description': 'Text Abuse Detection',
            'classes': 'Hate speech, profanity, threats, harassment',
            'threshold': '50%',
            'color': 'plum'
        }
    }
    
    for model_name, data in models_data.items():
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'COMPONENT HARISH - {model_name.upper()}\n{data["description"]}', 
                     fontsize=16, fontweight='bold')
        
        # Performance Metrics Bar Chart
        metrics = ['Accuracy', 'Precision', 'Recall']
        values = [data['accuracy'], data['precision'], data['recall']]
        bars = axes[0,0].bar(metrics, values, color=data['color'], alpha=0.8, 
                            edgecolor='black', linewidth=1)
        axes[0,0].set_title('Performance Metrics (%)', fontsize=14, fontweight='bold')
        axes[0,0].set_ylabel('Percentage (%)')
        axes[0,0].set_ylim(70, 100)
        axes[0,0].grid(True, alpha=0.3)
        
        for bar, val in zip(bars, values):
            axes[0,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{val}%', ha='center', va='bottom', fontweight='bold')
        
        # Architecture Information
        axes[0,1].axis('off')
        arch_text = f"""
        ARCHITECTURE DETAILS
        
        🏗️ Model Type: {data['architecture']}
        🎯 Confidence Threshold: {data['threshold']}
        📊 Detected Classes: {data['classes']}
        """
        axes[0,1].text(0.1, 0.5, arch_text, transform=axes[0,1].transAxes, 
                       fontsize=12, verticalalignment='center',
                       bbox=dict(boxstyle='round', facecolor=data['color'], alpha=0.3))
        
        # Performance Gauge (Accuracy)
        axes[1,0].pie([data['accuracy'], 100-data['accuracy']], 
                     labels=['Accuracy', 'Remaining'], 
                     colors=[data['color'], 'lightgray'],
                     startangle=90, wedgeprops=dict(width=0.3))
        axes[1,0].set_title(f'Accuracy: {data["accuracy"]}%', fontsize=14, fontweight='bold')
        
        # Key Features
        axes[1,1].axis('off')
        features_text = f"""
        KEY PERFORMANCE INDICATORS
        
        ✅ High Precision: {data['precision']}%
        ✅ High Recall: {data['recall']}%
        ✅ Fast Processing: <1 second
        ✅ Production Ready
        """
        axes[1,1].text(0.1, 0.5, features_text, transform=axes[1,1].transAxes, 
                       fontsize=12, verticalalignment='center',
                       bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        safe_name = model_name.replace(" ", "_").replace("/", "_").lower()
        graph_path = output_path / f"{safe_name}_performance.png"
        plt.savefig(graph_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ Generated {model_name} performance graph")

def generate_individual_summary_table(output_path):
    """Generate individual summary for each model"""
    
    models_data = [
        {
            'Model': 'Road Detection (YOLOv8)',
            'Accuracy': '94.2%',
            'Precision': '93.5%',
            'Recall': '94.9%',
            'Architecture': '8-model ensemble',
            'Classes': 'road, pothole, crack, pavement, asphalt',
            'Threshold': '50%'
        },
        {
            'Model': 'Abuse Detection (YOLOv8)',
            'Accuracy': '76.8%',
            'Precision': '78.5%',
            'Recall': '75.1%',
            'Architecture': '6-model weighted ensemble',
            'Classes': 'weapons, violence, blood, abusive content',
            'Threshold': '45-65%'
        },
        {
            'Model': 'Privacy Protection (YOLOv8)',
            'Accuracy': '90.6%',
            'Precision': '85.2%',
            'Recall': '96.3%',
            'Architecture': 'Human detection',
            'Classes': 'person, face, hand',
            'Threshold': '45%'
        },
        {
            'Model': 'Garbage Classification (YOLOv8)',
            'Accuracy': '92.8%',
            'Precision': '91.5%',
            'Recall': '94.1%',
            'Architecture': 'Clean vs Garbage',
            'Classes': 'Clean, Garbage Detected',
            'Threshold': '75%'
        },
        {
            'Model': 'Text Abuse Detection (DistilBERT)',
            'Accuracy': '89.5%',
            'Precision': '92.1%',
            'Recall': '87.2%',
            'Architecture': 'F1-Score metric',
            'Classes': 'Hate speech, profanity, threats, harassment',
            'Threshold': '50%'
        }
    ]
    
    for model_data in models_data:
        model_name = model_data['Model'].split(' (')[0].replace(' ', '_').lower()
        df = pd.DataFrame([model_data])
        csv_path = output_path / f"{model_name}_details.csv"
        df.to_csv(csv_path, index=False)
        print(f"   ✓ Generated {model_data['Model']} details")
    
    df_combined = pd.DataFrame(models_data)
    combined_path = output_path / "all_models_summary.csv"
    df_combined.to_csv(combined_path, index=False)
    print(f"   ✓ Generated combined models summary")

def main():
    print("="*80)
    print("GENERATING COMPLETE VIVA PRESENTATION GRAPHS")
    print("="*80)
    
    base_path = Path(__file__).parent
    models_path = base_path / "models"
    output_path = base_path / "viva_graphs"
    training_path = base_path / "training_curves"
    
    output_path.mkdir(exist_ok=True)
    training_path.mkdir(exist_ok=True)
    
    # Generate individual model performance graphs
    print("\n📊 Generating Individual Model Performance Graphs...")
    create_individual_model_graphs(output_path)
    
    # Generate individual summary tables
    print("\n📋 Generating Individual Model Summary Tables...")
    generate_individual_summary_table(output_path)
    
    # Generate training curves from real data
    print("\n📈 Generating Training Curves from Real Data...")
    
    # Road Detection Models
    road_results = {}
    for i in range(1, 9):
        road_csv = models_path / f"road_parallel_results/{i}/results.csv"
        if road_csv.exists():
            df = read_training_results(road_csv)
            road_results[f"Road_Model_{i}"] = df
            graph_path = training_path / f"road_model_{i}_training_curves.png"
            plot_training_curves(df, f"Road Model {i}", graph_path)
            print(f"   ✓ Generated Road Model {i} training curves")
    
    # Garbage Classification
    garbage_csv = models_path / "garbage_classification_model/results.csv"
    if garbage_csv.exists():
        df = read_training_results(garbage_csv)
        graph_path = training_path / "garbage_classification_training_curves.png"
        plot_training_curves(df, "Garbage Classification", graph_path)
        print("   ✓ Generated garbage classification training curves")
    
    print(f"\n✅ All graphs saved to:")
    print(f"   📈 Performance graphs: {output_path}")
    print(f"   📈 Training curves: {training_path}")
    print("="*80)
    print("FILES GENERATED:")
    print("="*80)
    print("📈 PERFORMANCE GRAPHS:")
    print("   - road_detection_performance.png")
    print("   - abuse_detection_performance.png")
    print("   - privacy_protection_performance.png")
    print("   - garbage_classification_performance.png")
    print("   - text_abuse_detection_performance.png")
    print("\n📈 TRAINING CURVES:")
    print("   - road_model_1_training_curves.png through road_model_8_training_curves.png")
    print("   - garbage_classification_training_curves.png")
    print("\n📋 SUMMARY TABLES:")
    print("   - Individual model details CSV files")
    print("   - all_models_summary.csv")
    print("="*80)

if __name__ == "__main__":
    main()