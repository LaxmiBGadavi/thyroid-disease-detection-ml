# Intelligent Systems for Thyroid Disease Detection Using Machine Learning

## 📌 Project Overview

This project uses Machine Learning algorithms to detect and classify thyroid conditions based on clinical and laboratory test results. It aims to support thyroid disease analysis by identifying patterns in patient data and predicting whether a case belongs to the Normal, Hyperthyroidism, or Hypothyroidism class.

The project uses the **XGBoost classification algorithm** to build a predictive model and evaluate its performance on thyroid-related data.

## 🎯 Objectives

- Analyze thyroid-related clinical and laboratory data.
- Develop a Machine Learning model for thyroid disease classification.
- Predict thyroid condition categories based on input features.
- Evaluate model performance using classification metrics.
- Explore how AI and Machine Learning can support healthcare data analysis.

## 🛠️ Technologies Used

- **Programming Language:** Python
- **Machine Learning:** XGBoost, Random Forest Scikit-learn
- **Data Processing:** Pandas, NumPy
- **Model Evaluation:** Accuracy, Precision, Recall, F1-score
- **Backend:** Flask 
- **Development Environment:** VS Code

## 📊 Dataset

The project uses a thyroid dataset containing clinical and laboratory test features.

Example features include:

- TSH
- T3
- TT4
- T4U
- FTI
- TBG
- Other available clinical features

The dataset is used to train and evaluate the classification model.

**Target classes:**
- Normal
- Hyperthyroidism
- Hypothyroidism

*Note: Update this section with the original dataset source and exact number of records and features before publishing.*

## ⚙️ Machine Learning Workflow

1. **Data Collection:** Load the thyroid dataset.
2. **Data Preprocessing:** Handle missing values, encode categorical variables, and prepare features.
3. **Feature Scaling:** Apply scaling if required by the selected model pipeline.
4. **Model Training:** Train an XGBoost classifier using the prepared data.
5. **Model Evaluation:** Measure performance using accuracy and classification metrics.
6. **Prediction:** Use the trained model to classify thyroid cases from input data.

## 🤖 Algorithm Used

### XGBoost Classifier

XGBoost is a gradient-boosting algorithm that builds an ensemble of decision trees. It is used in this project to learn patterns in thyroid-related data and predict the target class.

The model was configured with parameters such as:

- Number of estimators: 300
- Maximum tree depth: 6
- Learning rate: 0.05
- Subsample: 0.8
- Column sampling by tree: 0.8

These parameters should match the final training code in the repository.

## 📈 Model Performance

The model achieved a previously reported accuracy of **97.73%** during project evaluation.

Evaluation can include:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

## 📁 Project Structure

```text
thyroid-disease-detection-ml/
│
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
├── .gitignore
├── models/
│   ├── xgb_thyroid_model.pkl
│   ├── label_encoder.pkl
│   └── scaler.pkl
└── data/
    └── thyroid_balanced_6000_clean.csv
```


## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/LaxmiBGadavi/thyroid-disease-detection-ml
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

## 🔮 Future Enhancements

- Develop a user-friendly web interface for predictions.
- Add more robust model validation and explainability.
- Compare XGBoost with other classification algorithms.
- Improve handling of missing values and imbalanced data.
- Deploy the application for demonstration and educational use.

## ⚠️ Disclaimer

This project is intended for educational and research purposes only. Its predictions are not a substitute for professional medical advice, diagnosis, or treatment. Clinical decisions should be made by qualified healthcare professionals.

## 👩‍💻 Author

**Laxmi B. Gadavi**

## ⭐ Acknowledgements

Thanks to the open-source Python and Machine Learning communities for the tools and libraries used in this project.

