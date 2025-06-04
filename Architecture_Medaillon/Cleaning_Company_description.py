import pandas as pd

df = pd.read_csv('bronze/Company_description.csv')
df = df.drop(columns=['Unnamed: 0'])