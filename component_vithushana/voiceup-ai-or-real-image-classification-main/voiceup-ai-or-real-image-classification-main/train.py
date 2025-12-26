import os
import time
import csv

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import ResNet50_Weights

from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages  # 🔹 for single PDF


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_dataloaders(data_dir, batch_size=32):
    train_dir = os.path.join(data_dir, "train")
    val_dir = os.path.join(data_dir, "val")
    test_dir = os.path.join(data_dir, "test")

    # 🔹 Train transforms (with augmentation)
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])

    # 🔹 Eval transforms (val + test)
    eval_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=eval_transform)
    test_dataset = datasets.ImageFolder(test_dir, transform=eval_transform)

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=2
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=2
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=2
    )

    return train_loader, val_loader, test_loader, train_dataset.classes


def build_model(num_classes=2, freeze_backbone=True):
    """
    ResNet-50 with pretrained ImageNet weights.
    Last FC layer is replaced by a num_classes output.
    """
    model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    return model


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (preds == labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


def evaluate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (preds == labels).sum().item()

            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc, all_labels, all_preds


# ---------- Helpers for CSV + graphs ----------

def save_training_history_csv(history, out_path):
    fieldnames = ["epoch", "train_loss", "train_acc", "val_loss", "val_acc"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in history:
            writer.writerow(row)


def plot_curves(history, out_dir):
    epochs = [h["epoch"] for h in history]
    train_loss = [h["train_loss"] for h in history]
    val_loss = [h["val_loss"] for h in history]
    train_acc = [h["train_acc"] for h in history]
    val_acc = [h["val_acc"] for h in history]

    # Loss curve
    plt.figure()
    plt.plot(epochs, train_loss, label="Train Loss")
    plt.plot(epochs, val_loss, label="Val Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training & Validation Loss")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "loss_curve.png"))
    plt.close()

    # Accuracy curve
    plt.figure()
    plt.plot(epochs, train_acc, label="Train Acc")
    plt.plot(epochs, val_acc, label="Val Acc")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Training & Validation Accuracy")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "accuracy_curve.png"))
    plt.close()


def plot_confusion_matrix(cm, class_names, out_path):
    plt.figure()
    plt.imshow(cm, interpolation="nearest", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.colorbar()
    tick_marks = range(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)

    thresh = cm.max() / 2.0
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            plt.text(
                j, i, format(cm[i, j], "d"),
                horizontalalignment="center",
                color="white" if cm[i, j] > thresh else "black"
            )

    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


# ---------- NEW: Single PDF report ----------

def save_pdf_report(
    history, test_loss, test_acc, report_str, cm, class_names, out_path
):
    epochs = [h["epoch"] for h in history]
    train_loss = [h["train_loss"] for h in history]
    val_loss = [h["val_loss"] for h in history]
    train_acc = [h["train_acc"] for h in history]
    val_acc = [h["val_acc"] for h in history]

    with PdfPages(out_path) as pdf:
        # Page 1 – Summary text
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4-ish
        ax.axis("off")
        summary_text = (
            "VOICE UP – AI vs Real Image Classifier (ResNet-50)\n\n"
            f"Test Loss: {test_loss:.4f}\n"
            f"Test Accuracy: {test_acc:.4f}\n\n"
            "Classes: " + ", ".join(class_names) + "\n\n"
            "Classification Report:\n\n"
            + report_str
        )
        ax.text(0.03, 0.97, summary_text, va="top", ha="left", wrap=True, fontsize=9)
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2 – Loss curves
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(epochs, train_loss, label="Train Loss")
        ax.plot(epochs, val_loss, label="Val Loss")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title("Training & Validation Loss")
        ax.grid(True)
        ax.legend()
        pdf.savefig(fig)
        plt.close(fig)

        # Page 3 – Accuracy curves
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(epochs, train_acc, label="Train Acc")
        ax.plot(epochs, val_acc, label="Val Acc")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Accuracy")
        ax.set_title("Training & Validation Accuracy")
        ax.grid(True)
        ax.legend()
        pdf.savefig(fig)
        plt.close(fig)

        # Page 4 – Confusion matrix
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
        ax.set_title("Confusion Matrix")
        fig.colorbar(im, ax=ax)
        tick_marks = range(len(class_names))
        ax.set_xticks(tick_marks)
        ax.set_yticks(tick_marks)
        ax.set_xticklabels(class_names, rotation=45, ha="right")
        ax.set_yticklabels(class_names)

        thresh = cm.max() / 2.0
        for i in range(len(class_names)):
            for j in range(len(class_names)):
                ax.text(
                    j, i, format(cm[i, j], "d"),
                    ha="center",
                    va="center",
                    color="white" if cm[i, j] > thresh else "black",
                )

        ax.set_ylabel("True label")
        ax.set_xlabel("Predicted label")
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)


# ---------- MAIN ----------

def main():
    data_dir = os.path.join("data", "dataset")
    num_epochs = 10
    batch_size = 8
    learning_rate = 1e-4

    os.makedirs("results", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    device = get_device()
    print(f"Using device: {device}")

    train_loader, val_loader, test_loader, class_names = get_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
    )
    print("Classes:", class_names)

    model = build_model(num_classes=len(class_names), freeze_backbone=False)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_val_acc = 0.0
    best_model_state = None

    history = []

    for epoch in range(1, num_epochs + 1):
        start_time = time.time()

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_acc, _, _ = evaluate(
            model, val_loader, criterion, device
        )

        elapsed = time.time() - start_time
        print(
            f"Epoch [{epoch}/{num_epochs}] "
            f"- Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} "
            f"- Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f} "
            f"- Time: {elapsed:.1f}s"
        )

        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
        })

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = model.state_dict()

    # 🔹 Save CSV + curves
    csv_path = os.path.join("results", "training_history.csv")
    save_training_history_csv(history, csv_path)
    print(f"\nTraining history saved to: {csv_path}")

    plot_curves(history, "results")
    print("Loss & accuracy curves saved to: results/loss_curve.png & results/accuracy_curve.png")

    # 🔹 Load best model
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    # 🔹 Test eval
    test_loss, test_acc, test_labels, test_preds = evaluate(
        model, test_loader, criterion, device
    )
    print("\n=== Test Results ===")
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Acc : {test_acc:.4f}")

    report = classification_report(test_labels, test_preds, target_names=class_names)
    cm = confusion_matrix(test_labels, test_preds)

    print("\nClassification Report:")
    print(report)

    print("\nConfusion Matrix:")
    print(cm)

    # 🔹 Save text report
    with open(os.path.join("results", "classification_report.txt"), "w") as f:
        f.write("=== Test Results ===\n")
        f.write(f"Test Loss: {test_loss:.4f}\n")
        f.write(f"Test Acc : {test_acc:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)

    cm_path = os.path.join("results", "confusion_matrix.png")
    plot_confusion_matrix(cm, class_names, cm_path)
    print("Classification report & confusion matrix saved in 'results' folder.")

    # 🔹 SINGLE PDF REPORT
    pdf_path = os.path.join("results", "report.pdf")
    save_pdf_report(history, test_loss, test_acc, report, cm, class_names, pdf_path)
    print(f"Full PDF report saved to: {pdf_path}")

    # 🔹 Model weights
    model_path = os.path.join("models", "resnet50_ai_vs_real.pth")
    torch.save(model.state_dict(), model_path)
    print(f"\nModel saved to: {model_path}")


if __name__ == "__main__":
    main()
