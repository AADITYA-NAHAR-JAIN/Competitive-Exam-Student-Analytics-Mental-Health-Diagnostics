import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from utils import COLOR_PALETTE, save_figure


class DataCleaner:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.raw_df = None
        self.df = None
        self.quality_report = {}
        self.cleaning_log = []
        self.engineered_features = []

    def load_data(self):
        """Loads data and initial shape."""
        self.raw_df = pd.read_csv(self.filepath)
        self.df = self.raw_df.copy()
        print(f"Data Loaded Successfully. Shape: {self.df.shape}")

    def assess_quality(self) -> dict:
        """Phase 2: Generates comprehensive Data Quality Assessment report."""
        total_rows = len(self.df)
        null_counts = self.df.isnull().sum()
        null_pct = (null_counts / total_rows) * 100

        dup_count = self.df.duplicated().sum()
        constant_cols = [col for col in self.df.columns if self.df[col].nunique() == 1]
        high_cardinality = [col for col in self.df.columns if self.df[col].nunique() > 50 and self.df[col].dtype == 'object']

        quality_summary = pd.DataFrame({
            'Dtype': self.df.dtypes.astype(str),
            'Null_Count': null_counts,
            'Null_Percentage': null_pct.round(2),
            'Unique_Values': self.df.nunique()
        })

        self.quality_report = {
            'total_rows': total_rows,
            'total_cols': len(self.df.columns),
            'duplicate_records': int(dup_count),
            'constant_columns': constant_cols,
            'high_cardinality_columns': high_cardinality,
            'column_summary': quality_summary.to_dict(orient='index')
        }

        # Generate Missingno Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        msno.matrix(self.df, sparkline=False, color=(0.0, 0.2, 0.4), ax=ax)
        plt.title('Data Quality Assessment - Missing Value Matrix', fontsize=14, pad=20, fontweight='bold', color=COLOR_PALETTE['primary'])
        save_figure(fig, 'missing_data_matrix.png')

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        msno.bar(self.df, color=COLOR_PALETTE['secondary'], ax=ax2)
        plt.title('Data Quality Assessment - Data Completeness Bar Chart', fontsize=14, pad=20, fontweight='bold', color=COLOR_PALETTE['primary'])
        save_figure(fig2, 'missing_data_bar.png')

        return self.quality_report

    def clean_data(self) -> pd.DataFrame:
        """Phase 3: Intelligent cleaning, feature engineering, and preprocessing."""
        print("Starting Intelligent Data Cleaning...")

        # 1. Drop completely empty / redundant columns (>70% missing)
        null_pct = (self.df.isnull().sum() / len(self.df)) * 100
        cols_to_drop = null_pct[null_pct > 70.0].index.tolist()
        
        # Also drop uninformative default trailing columns like Column 14, 15, 16
        for col in self.df.columns:
            if 'Column' in col or col in cols_to_drop:
                if col not in cols_to_drop:
                    cols_to_drop.append(col)

        cols_to_drop = list(set(cols_to_drop))
        if cols_to_drop:
            self.df.drop(columns=cols_to_drop, inplace=True)
            self.cleaning_log.append(f"Dropped columns with >70% missing data or uninformative headers: {cols_to_drop}")

        # 2. Remove duplicates
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed_dups = initial_rows - len(self.df)
        self.cleaning_log.append(f"Detected and removed {removed_dups} duplicate row(s).")

        # 3. Rename columns to standardized, clean identifiers for clean programming
        column_mapping = {
            'Timestamp': 'Timestamp',
            'What is your age?': 'Age_Group',
            'What is your gender identification?': 'Gender',
            'Which major competitive exam are you primarily preparing for / have taken?': 'Target_Exam',
            'How many times have you attempted this specific competitive exam?': 'Attempt_Count',
            'How would you describe your score/performance in your most recent attempt?': 'Performance_Category',
            'If you comfortable sharing, what was your approximate percentile or score range in your last attempt? (out of 100)': 'Raw_Score_Text',
            'On average, how many hours per day do you dedicate to self-study and classes?': 'Study_Hours_Category',
            'How many hours of sleep do you get on an average night during peak exam preparation?': 'Sleep_Hours_Category',
            'What is your primary method of test preparation?': 'Prep_Method',
            'On a scale of 1 to 10, how would you rate your overall daily stress level during the exam preparation phase?': 'Stress_Level',
            'Have you experienced any of the following physical or emotional symptoms regularly during your preparation? ': 'Physical_Emotional_Symptoms',
            'What do you feel is the primary source of your competitive exam stress?': 'Stress_Primary_Source'
        }
        self.df.rename(columns=column_mapping, inplace=True)
        self.cleaning_log.append("Standardized column names into structured variable identifiers.")

        # 4. Text Cleaning for object columns
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
                self.df[col] = self.df[col].replace({'nan': np.nan, 'None': np.nan, 'Na': np.nan, 'NA': np.nan, 'N/A': np.nan})

        self.cleaning_log.append("Performed text normalization: trimmed whitespace, normalized spaces, and converted pseudo-null strings to NaN.")

        # 5. Extract Numeric Scores from free text Raw_Score_Text
        def extract_score(text):
            if pd.isna(text):
                return np.nan
            text_str = str(text).lower()
            # Extract first floating point or integer number
            match = re.search(r'\d+(\.\d+)?', text_str)
            if match:
                val = float(match.group(0))
                if 0 <= val <= 100:
                    return val
            return np.nan

        self.df['Percentile_Score'] = self.df['Raw_Score_Text'].apply(extract_score)
        self.cleaning_log.append("Extracted numerical percentile scores into feature 'Percentile_Score'.")

        # 6. Convert Ordinal Categories into Numeric Quantitative Features
        study_map = {
            'less than 4': 2.5,
            '4-7 hours': 5.5,
            '7-11 hours': 9.0,
            '12+ hours': 13.0
        }
        sleep_map = {
            'less than 5 hours': 4.0,
            '5-6 hours': 5.5,
            '7-8 hours': 7.5,
            'more than 8 hours': 9.5
        }
        self.df['Study_Hours_Num'] = self.df['Study_Hours_Category'].map(study_map)
        self.df['Sleep_Hours_Num'] = self.df['Sleep_Hours_Category'].map(sleep_map)
        self.cleaning_log.append("Converted categorical study and sleep hour bands into numerical midpoints ('Study_Hours_Num', 'Sleep_Hours_Num').")

        # 7. Impute Missing Values
        # Numeric columns: Median
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if self.df[col].isnull().sum() > 0:
                median_val = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_val)
                self.cleaning_log.append(f"Imputed missing values in numeric column '{col}' using Median ({median_val}).")

        # Categorical columns: Mode
        categorical_cols = [c for c in self.df.columns if self.df[c].dtype == 'object']
        for col in categorical_cols:
            if col != 'Raw_Score_Text' and self.df[col].isnull().sum() > 0:
                mode_val = self.df[col].mode()[0] if not self.df[col].mode().empty else "Unknown"
                self.df[col] = self.df[col].fillna(mode_val)
                self.cleaning_log.append(f"Imputed missing values in categorical column '{col}' using Mode ('{mode_val}').")

        # 8. Datetime Parsing & Feature Engineering
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        self.df['Prep_Year'] = self.df['Timestamp'].dt.year.fillna(2026).astype(int)
        self.df['Prep_Month'] = self.df['Timestamp'].dt.month.fillna(6).astype(int)
        self.df['Prep_Day'] = self.df['Timestamp'].dt.day.fillna(1).astype(int)
        self.df['Prep_Weekday'] = self.df['Timestamp'].dt.day_name().fillna('Monday')

        # Multi-select Symptom & Stress source metrics
        self.df['Symptom_Count'] = self.df['Physical_Emotional_Symptoms'].apply(
            lambda x: 0 if pd.isna(x) or str(x).lower() == 'none' else len(str(x).split(','))
        )
        self.df['Stress_Source_Count'] = self.df['Stress_Primary_Source'].apply(
            lambda x: 0 if pd.isna(x) or str(x).lower() == 'none' else len(str(x).split(','))
        )

        # Ratio and Flag Features
        self.df['Stress_Sleep_Ratio'] = (self.df['Stress_Level'] / self.df['Sleep_Hours_Num']).round(2)
        self.df['High_Stress_Flag'] = (self.df['Stress_Level'] >= 8).astype(int)
        self.df['Severe_Sleep_Deprived_Flag'] = (self.df['Sleep_Hours_Num'] <= 5.5).astype(int)

        self.engineered_features = ['Prep_Year', 'Prep_Month', 'Prep_Day', 'Prep_Weekday', 
                                    'Symptom_Count', 'Stress_Source_Count', 'Stress_Sleep_Ratio', 
                                    'High_Stress_Flag', 'Severe_Sleep_Deprived_Flag']
        self.cleaning_log.append(f"Engineered features: {self.engineered_features}")

        # 9. Outlier Analysis Visualization
        self._generate_outlier_plots()

        return self.df

    def _generate_outlier_plots(self):
        """Generates boxplots and outlier analysis tables."""
        num_cols = ['Stress_Level', 'Study_Hours_Num', 'Sleep_Hours_Num', 'Symptom_Count', 'Stress_Sleep_Ratio']
        fig, axes = plt.subplots(1, len(num_cols), figsize=(16, 5))
        for i, col in enumerate(num_cols):
            sns.boxplot(y=self.df[col], ax=axes[i], color=COLOR_PALETTE['secondary'])
            axes[i].set_title(col, fontsize=11, fontweight='bold', color=COLOR_PALETTE['primary'])
            axes[i].set_ylabel('')
        plt.suptitle('Phase 3 - Outlier Identification Boxplots', fontsize=14, fontweight='bold', y=1.02, color=COLOR_PALETTE['primary'])
        save_figure(fig, 'outlier_boxplots.png')

    def export_datasets(self, output_dir: str = '.'):
        """Phase 3: Encodes, scales, and exports cleaned and scaled datasets."""
        os.makedirs('cleaned_data', exist_ok=True)
        
        # Save main cleaned CSV
        cleaned_path = os.path.join(output_dir, 'cleaned_dataset.csv')
        self.df.to_csv(cleaned_path, index=False)
        self.df.to_csv(os.path.join('cleaned_data', 'cleaned_dataset.csv'), index=False)
        print(f"Saved Cleaned Dataset to {cleaned_path}")

        # Create Encoded and Scaled Dataset
        df_encoded = self.df.copy()
        label_encoders = {}
        cat_cols = df_encoded.select_dtypes(include=['object']).columns

        for col in cat_cols:
            if col != 'Timestamp':
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                label_encoders[col] = le

        # Drop Datetime object for scaling
        df_numeric = df_encoded.select_dtypes(include=[np.number])

        scaler_std = StandardScaler()
        df_std = pd.DataFrame(scaler_std.fit_transform(df_numeric), columns=df_numeric.columns)

        scaler_minmax = MinMaxScaler()
        df_minmax = pd.DataFrame(scaler_minmax.fit_transform(df_numeric), columns=df_numeric.columns)

        scaled_path = os.path.join(output_dir, 'scaled_dataset.csv')
        df_std.to_csv(scaled_path, index=False)
        df_std.to_csv(os.path.join('cleaned_data', 'scaled_dataset.csv'), index=False)
        df_minmax.to_csv(os.path.join('cleaned_data', 'minmax_scaled_dataset.csv'), index=False)
        print(f"Saved Scaled Dataset to {scaled_path}")

        return cleaned_path, scaled_path


if __name__ == '__main__':
    cleaner = DataCleaner('data.csv.csv')
    cleaner.load_data()
    report = cleaner.assess_quality()
    df_clean = cleaner.clean_data()
    cleaner.export_datasets()
