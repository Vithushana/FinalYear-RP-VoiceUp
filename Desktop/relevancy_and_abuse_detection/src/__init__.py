# AI Detection System Package

# Integrate training results
class TrainingResultsIntegrator:
    def __init__(self, results_dir):
        self.results_dir = results_dir
        self.models = {}

    def load_models(self):
        """Load all models from the results directory"""
        for i in range(1, 9):
            best_model_path = os.path.join(self.results_dir, f"best_{i}.pt")
            last_model_path = os.path.join(self.results_dir, f"last_{i}.pt")

            if os.path.exists(best_model_path):
                self.models[f"best_{i}"] = best_model_path
                print(f"✅ Loaded best model: {best_model_path}")
            else:
                print(f"❌ Best model not found: {best_model_path}")

            if os.path.exists(last_model_path):
                self.models[f"last_{i}"] = last_model_path
                print(f"✅ Loaded last model: {last_model_path}")
            else:
                print(f"❌ Last model not found: {last_model_path}")

    def summarize_results(self):
        """Generate high-level summary of training results"""
        summary = {
            "total_models": len(self.models),
            "best_models": [key for key in self.models if key.startswith("best")],
            "last_models": [key for key in self.models if key.startswith("last")]
        }
        print("📊 High-Level Training Results Summary:")
        print(summary)
        return summary

# Example usage
import os
results_dir = "C:\\Users\\Admin pc\\Desktop\\relevancy_and_abuse_detection\\road_full\\road_training_results"
integrator = TrainingResultsIntegrator(results_dir)
integrator.load_models()
summary = integrator.summarize_results()
