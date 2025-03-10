import os
import pandas as pd
import matplotlib.pyplot as plt

# Define base path for datasets
base_path = "/content/drive/MyDrive/data/"  # Updated to your Google Drive path

# Dictionary to store processed data
dataset_dicts = {}

# Process each file in the directory
for ds_fname in os.listdir(base_path):
    tmp_path = os.path.join(base_path, ds_fname)
    key = ds_fname.split('.')[0]

    # Read CSV file with headers
    tmp_df = pd.read_csv(tmp_path)

    # Extract PRN values (first 8 available from every 11th column)
    prn_li = [int(tmp_df.iloc[1, i]) for i in range(1, min(88, len(tmp_df.columns)), 11)][:8]

    # Create a dictionary for the dataset
    dataset_dicts[key] = {
        int(prn_li[i]): tmp_df.iloc[100:, i*11:(i+1)*11]  # Adjust based on the new header structure
        .iloc[:, 5:].diff().fillna(0)  # Compute differences and fill NaN values
        for i in range(len(prn_li))  # Adjusted to avoid index errors
    }

    dataset_dicts[key]['prn'] = prn_li  # Store PRN values for reference

# Assign dataset variables (up to 7 datasets)
dataset_keys = list(dataset_dicts.keys())
if len(dataset_keys) >= 7:
    cs_dict, ds1_dict, ds2_dict, ds3_dict, ds4_dict, ds7_dict, ds8_dict = [dataset_dicts[k] for k in dataset_keys[:7]]
else:
    print("Warning: Less than 7 datasets found!")

# Function to compare CleanStatic vs Spoofed GNSS signals and save outputs
def compare_side_by_side(cs_dict, ds_dict, key, save_name, runtime_dir="/content/drive/MyDrive/output_comparisons"):
    """Compare CleanStatic vs Spoofed GNSS signals and save outputs."""

    # Ensure output directory exists
    os.makedirs(runtime_dir, exist_ok=True)

    # Get first available PRN
    clean_prn = cs_dict['prn'][0]
    spoofed_prn = ds_dict['prn'][0]

    # Extract signal data
    clean_signal = cs_dict[clean_prn][key]
    spoofed_signal = ds_dict[spoofed_prn][key]

    # Create side-by-side subplots
    fig, axes = plt.subplots(1, 2, figsize=(7, 3), sharey=True)
    fig.suptitle(f"Comparison of {key}", fontsize=12)

    # Plot CleanStatic
    axes[0].plot(clean_signal, color='blue')
    axes[0].set_title("CleanStatic", fontsize=10)
    axes[0].set_xlabel("Time", fontsize=9)
    axes[0].set_ylabel("Signal Strength", fontsize=9)
    axes[0].tick_params(axis='both', labelsize=8)

    # Plot Spoofed
    axes[1].plot(spoofed_signal, color='red')
    axes[1].set_title("Spoofed", fontsize=10)
    axes[1].set_xlabel("Time", fontsize=9)
    axes[1].tick_params(axis='both', labelsize=8)

    plt.tight_layout()

    # Save plots
    pdf_runtime = os.path.join(runtime_dir, f"{save_name}.pdf")
    png_runtime = os.path.join(runtime_dir, f"{save_name}.png")
    plt.savefig(pdf_runtime, format="pdf", bbox_inches="tight")
    plt.savefig(png_runtime, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Saved: {pdf_runtime}, {png_runtime}")

# Example comparisons
compare_side_by_side(cs_dict, ds3_dict, "prompt_i", "comparison_prompt_i")
compare_side_by_side(cs_dict, ds3_dict, "prompt_q", "comparison_prompt_q")
compare_side_by_side(cs_dict, ds3_dict, "cn0_db_hz", "comparison_cn0_db_hz")
compare_side_by_side(cs_dict, ds3_dict, "carrier_doppler_hz", "comparison_carrier_doppler_hz")

# Create and save X_clean dataset (replacing X_train)
X_clean = pd.concat([cs_dict[3], cs_dict[6], cs_dict[7], cs_dict[10], cs_dict[13], cs_dict[16], cs_dict[19], cs_dict[23]]).reset_index().drop('index', axis=1)
X_clean['label'] = 0  # Add label column for X_clean (label = 0 for CleanStatic)
X_clean.to_csv('X_clean_dataset.csv', index=False)
print("X_clean has been saved as 'X_clean_dataset.csv'.")

# Create and save X_ds3 dataset (replacing X_test)
X_ds3 = pd.concat([ds3_dict[3], ds3_dict[6], ds3_dict[7], ds3_dict[10], ds3_dict[13], ds3_dict[16], ds3_dict[19], ds3_dict[23]]).reset_index().drop('index', axis=1)
X_ds3['label'] = 1  # Add label column for X_ds3 (label = 1 for Spoofed)
X_ds3.to_csv('X_ds3_dataset.csv', index=False)
print("X_ds3 has been saved as 'X_ds3_dataset.csv'.")

# Create and save the final labeled dataset (X_clean + X_ds3)
final_labeled_dataset = pd.concat([X_clean, X_ds3], ignore_index=True)
final_labeled_dataset.to_csv('labeled_dataset.csv', index=False)
print("Final labeled dataset has been saved as 'labeled_dataset.csv'.")
