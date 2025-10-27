#!/usr/bin/env python3
"""
Generate Training Metrics Visualizations

Creates publication-ready graphs for dissertation:
- Training/validation loss curves
- Learning rate schedule
- Gradient norm progression
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

# Set style for academic publications
plt.style.use("seaborn-v0_8-paper")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["font.size"] = 10
plt.rcParams["font.family"] = "serif"


def load_training_data():
    """Load training metrics from checkpoint."""
    checkpoint_path = Path(
        "models/t5-function-call-finetuned/checkpoint-150/trainer_state.json"
    )

    with open(checkpoint_path, "r") as f:
        state = json.load(f)

    return state["log_history"]


def extract_metrics(log_history):
    """Extract training metrics into separate arrays."""
    epochs_train = []
    train_losses = []
    epochs_eval = []
    eval_losses = []
    learning_rates = []
    gradient_norms = []

    for entry in log_history:
        epoch = entry.get("epoch", 0)

        # Training loss
        if "loss" in entry:
            epochs_train.append(epoch)
            train_losses.append(entry["loss"])

        # Evaluation loss
        if "eval_loss" in entry:
            epochs_eval.append(epoch)
            eval_losses.append(entry["eval_loss"])

        # Learning rate
        if "learning_rate" in entry:
            learning_rates.append((epoch, entry["learning_rate"]))

        # Gradient norm
        if "grad_norm" in entry:
            gradient_norms.append((epoch, entry["grad_norm"]))

    return {
        "epochs_train": epochs_train,
        "train_losses": train_losses,
        "epochs_eval": epochs_eval,
        "eval_losses": eval_losses,
        "learning_rates": learning_rates,
        "gradient_norms": gradient_norms,
    }


def plot_loss_curves(metrics, output_dir):
    """Create training and validation loss curves."""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Plot training loss
    ax.plot(
        metrics["epochs_train"],
        metrics["train_losses"],
        "o-",
        label="Training Loss",
        color="#2E86AB",
        linewidth=2,
        markersize=4,
    )

    # Plot validation loss
    ax.plot(
        metrics["epochs_eval"],
        metrics["eval_losses"],
        "s-",
        label="Validation Loss",
        color="#A23B72",
        linewidth=2,
        markersize=6,
    )

    # Formatting
    ax.set_xlabel("Epoch", fontsize=12, fontweight="bold")
    ax.set_ylabel("Loss", fontsize=12, fontweight="bold")
    ax.set_title(
        "T5 Function Call Model - Training Progress",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.legend(loc="upper right", fontsize=11, frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xlim(0, 10.5)

    # Add annotation for final loss
    final_epoch = metrics["epochs_eval"][-1]
    final_loss = metrics["eval_losses"][-1]
    ax.annotate(
        f"Final: {final_loss:.4f}",
        xy=(final_epoch, final_loss),
        xytext=(final_epoch - 2, final_loss + 0.3),
        arrowprops=dict(arrowstyle="->", color="#A23B72", lw=1.5),
        fontsize=10,
        fontweight="bold",
        color="#A23B72",
    )

    plt.tight_layout()
    plt.savefig(output_dir / "loss_curves.png", dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_dir / 'loss_curves.png'}")
    plt.close()


def plot_learning_rate_schedule(metrics, output_dir):
    """Plot learning rate schedule over training."""
    fig, ax = plt.subplots(figsize=(8, 5))

    epochs_lr = [x[0] for x in metrics["learning_rates"]]
    lr_values = [x[1] for x in metrics["learning_rates"]]

    ax.plot(epochs_lr, lr_values, "o-", color="#F18F01", linewidth=2, markersize=4)

    # Mark warmup phase
    warmup_end = 1.0  # 10% of 10 epochs
    ax.axvline(x=warmup_end, color="gray", linestyle="--", alpha=0.5, linewidth=1.5)
    ax.text(
        warmup_end + 0.2,
        max(lr_values) * 0.9,
        "Warmup End",
        fontsize=10,
        color="gray",
        fontstyle="italic",
    )

    ax.set_xlabel("Epoch", fontsize=12, fontweight="bold")
    ax.set_ylabel("Learning Rate", fontsize=12, fontweight="bold")
    ax.set_title(
        "Learning Rate Schedule (Linear Warmup + Decay)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xlim(0, 10.5)
    ax.ticklabel_format(style="scientific", axis="y", scilimits=(0, 0))

    plt.tight_layout()
    plt.savefig(output_dir / "learning_rate_schedule.png", dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_dir / 'learning_rate_schedule.png'}")
    plt.close()


def plot_gradient_norms(metrics, output_dir):
    """Plot gradient norm progression (shows training stability)."""
    fig, ax = plt.subplots(figsize=(8, 5))

    epochs_gn = [x[0] for x in metrics["gradient_norms"]]
    gn_values = [x[1] for x in metrics["gradient_norms"]]

    ax.plot(epochs_gn, gn_values, "o-", color="#06A77D", linewidth=2, markersize=4)

    # Add horizontal line at gradient clip threshold
    ax.axhline(
        y=1.0,
        color="red",
        linestyle="--",
        alpha=0.5,
        linewidth=1.5,
        label="Clip Threshold (1.0)",
    )

    ax.set_xlabel("Epoch", fontsize=12, fontweight="bold")
    ax.set_ylabel("Gradient Norm", fontsize=12, fontweight="bold")
    ax.set_title(
        "Gradient Norm Progression (Training Stability)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.legend(loc="upper right", fontsize=11, frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xlim(0, max(epochs_gn) + 0.5)

    plt.tight_layout()
    plt.savefig(output_dir / "gradient_norms.png", dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_dir / 'gradient_norms.png'}")
    plt.close()


def plot_combined_dashboard(metrics, output_dir):
    """Create a comprehensive dashboard with all metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Loss Curves (top-left)
    ax1 = axes[0, 0]
    ax1.plot(
        metrics["epochs_train"],
        metrics["train_losses"],
        "o-",
        label="Training",
        color="#2E86AB",
        linewidth=2,
        markersize=3,
    )
    ax1.plot(
        metrics["epochs_eval"],
        metrics["eval_losses"],
        "s-",
        label="Validation",
        color="#A23B72",
        linewidth=2,
        markersize=5,
    )
    ax1.set_xlabel("Epoch", fontweight="bold")
    ax1.set_ylabel("Loss", fontweight="bold")
    ax1.set_title("(a) Training Progress", fontweight="bold", loc="left")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, linestyle="--")

    # 2. Learning Rate (top-right)
    ax2 = axes[0, 1]
    epochs_lr = [x[0] for x in metrics["learning_rates"]]
    lr_values = [x[1] for x in metrics["learning_rates"]]
    ax2.plot(epochs_lr, lr_values, "o-", color="#F18F01", linewidth=2, markersize=3)
    ax2.axvline(x=1.0, color="gray", linestyle="--", alpha=0.5)
    ax2.set_xlabel("Epoch", fontweight="bold")
    ax2.set_ylabel("Learning Rate", fontweight="bold")
    ax2.set_title("(b) LR Schedule", fontweight="bold", loc="left")
    ax2.grid(True, alpha=0.3, linestyle="--")
    ax2.ticklabel_format(style="scientific", axis="y", scilimits=(0, 0))

    # 3. Gradient Norms (bottom-left)
    ax3 = axes[1, 0]
    epochs_gn = [x[0] for x in metrics["gradient_norms"]]
    gn_values = [x[1] for x in metrics["gradient_norms"]]
    ax3.plot(epochs_gn, gn_values, "o-", color="#06A77D", linewidth=2, markersize=3)
    ax3.axhline(y=1.0, color="red", linestyle="--", alpha=0.5, label="Clip Threshold")
    ax3.set_xlabel("Epoch", fontweight="bold")
    ax3.set_ylabel("Gradient Norm", fontweight="bold")
    ax3.set_title("(c) Gradient Stability", fontweight="bold", loc="left")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, linestyle="--")

    # 4. Loss Improvement (bottom-right)
    ax4 = axes[1, 1]
    # Calculate epoch-over-epoch improvement
    eval_improvements = []
    for i in range(1, len(metrics["eval_losses"])):
        prev_loss = metrics["eval_losses"][i - 1]
        curr_loss = metrics["eval_losses"][i]
        improvement_pct = ((prev_loss - curr_loss) / prev_loss) * 100
        eval_improvements.append(improvement_pct)

    improvement_epochs = metrics["epochs_eval"][1:]
    colors = ["green" if x > 0 else "red" for x in eval_improvements]
    ax4.bar(
        improvement_epochs,
        eval_improvements,
        color=colors,
        alpha=0.7,
        edgecolor="black",
    )
    ax4.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax4.set_xlabel("Epoch", fontweight="bold")
    ax4.set_ylabel("Improvement (%)", fontweight="bold")
    ax4.set_title("(d) Epoch-over-Epoch Improvement", fontweight="bold", loc="left")
    ax4.grid(True, alpha=0.3, linestyle="--", axis="y")

    fig.suptitle(
        "T5 Function Call Model - Training Metrics Dashboard",
        fontsize=16,
        fontweight="bold",
        y=0.995,
    )

    plt.tight_layout()
    plt.savefig(output_dir / "training_dashboard.png", dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_dir / 'training_dashboard.png'}")
    plt.close()


def main():
    """Generate all visualizations."""
    print("=" * 70)
    print("📊 Generating Training Metrics Visualizations")
    print("=" * 70)

    # Create output directory
    output_dir = Path("docs/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("\n📂 Loading training data...")
    log_history = load_training_data()
    metrics = extract_metrics(log_history)
    print(f"   ✅ Loaded {len(log_history)} log entries")

    # Generate plots
    print("\n🎨 Generating visualizations...")
    plot_loss_curves(metrics, output_dir)
    plot_learning_rate_schedule(metrics, output_dir)
    plot_gradient_norms(metrics, output_dir)
    plot_combined_dashboard(metrics, output_dir)

    print("\n" + "=" * 70)
    print("✅ All visualizations generated successfully!")
    print(f"📁 Location: {output_dir}")
    print("=" * 70)
    print("\n📋 Files created:")
    print("   1. loss_curves.png - Training/validation loss progression")
    print("   2. learning_rate_schedule.png - LR warmup and decay")
    print("   3. gradient_norms.png - Training stability metrics")
    print("   4. training_dashboard.png - Comprehensive 4-panel overview")
    print("\n💡 Use these in your dissertation figures!")
    print("=" * 70)


if __name__ == "__main__":
    main()
