import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('/Users/hritvikgupta/Downloads/Langchain-DataAnalysis-Tool/uploads/titanic_dataset.csv')

# Lowercase the column names
df.columns = df.columns.str.lower()

# Generate histogram
plt.hist(df[df['survived'] == 1]['age'], bins=20, alpha=0.5, label='Survived')
plt.hist(df[df['survived'] == 0]['age'], bins=20, alpha=0.5, label='Did not survive')
plt.xlabel('Age')
plt.ylabel('Count')
plt.title('Distribution of Age for Survived and Did not Survive')
plt.legend()

# Save the histogram
plt.savefig('/Users/hritvikgupta/Downloads/Langchain-DataAnalysis-Tool/static/retrived_data/image_new_header1.png')