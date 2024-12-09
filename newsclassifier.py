import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

class NewsClassifier:
    def __init__(self, file_path, desired_categories, min_samples=1014):
        self.file_path = file_path
        self.desired_categories = desired_categories
        self.min_samples = min_samples
        self.df = None
        self.label_encoder = None
        self.model = None

    def load_and_preprocess_data(self):
        # Load dataset
        self.df = pd.read_json(self.file_path)
        
        # Drop unnecessary columns
        self.df = self.df.drop(columns=['link', 'short_description', 'authors', 'date'])
        
        # Filter by desired categories
        self.df = self.df[self.df['category'].isin(self.desired_categories)]
        
        # Balancing the dataset
        balanced_df = []
        for category in self.desired_categories:
            balanced_df.append(self.df[self.df['category'] == category].sample(self.min_samples, random_state=2020))
        self.df = pd.concat(balanced_df, axis=0)

        # Encode category labels
        self.label_encoder = LabelEncoder()
        self.df['category_encoded'] = self.label_encoder.fit_transform(self.df['category'])

    def train_test_split(self, test_size=0.2, random_state=42):
        X = self.df['headline']
        y = self.df['category_encoded']
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

    def train_model(self, X_train, y_train):
        # Build the pipeline for Naive Bayes with CountVectorizer
        self.model = Pipeline([
            ('vectorize_bow', CountVectorizer(ngram_range=(1, 1))),
            ('MultiNb', MultinomialNB())
        ])
        # Train the model
        self.model.fit(X_train, y_train)

    def predict_category(self, headlines):
        # Predict category label
        predicted_labels = self.model.predict(headlines)
        # Convert label number back to category name
        return self.label_encoder.inverse_transform(predicted_labels)

# Example usage
if __name__ == "__main__":
    # Initialize classifier with the JSON file path and desired categories
    classifier = NewsClassifier('Repaired_News_Category_Dataset_v3.json', 
                                desired_categories=['COMEDY', 'SPORTS', 'CRIME', 'EDUCATION', 'TECH', 'BUSINESS'])
    
    # Load and preprocess the data
    classifier.load_and_preprocess_data()
    
    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = classifier.train_test_split()
    
    # Train the classifier
    classifier.train_model(X_train, y_train)
    
    # Predict a single headline
    prediction = classifier.predict_category(['Classified US Intelligence Leaked, Documents Show Israel\'s Plans For Iran'])
    
    # Output the prediction
    print(prediction)