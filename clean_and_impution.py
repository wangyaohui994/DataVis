import pandas as pd
import numpy as np

df = pd.read_csv("cars.csv")

#df.loc select all the rows or cells that meet the criterias
def clean_range(col, low, high):
    df.loc[(df[col] < low) | (df[col] > high), col] = np.nan

clean_range('Engine Size (l)', 0.8, 8.0)
clean_range('Cyl', 3, 16)
clean_range('Horsepower(HP)', 50, 1000)
clean_range('City Miles Per Gallon', 5, 80)
clean_range('Highway Miles Per Gallon', 10, 100)
clean_range('Weight', 1500, 10000)
clean_range('Wheel Base', 80, 150)
clean_range('Len', 120, 250)
clean_range('Width', 60, 90)
clean_range('Retail Price', 2000, 200000)
clean_range('Dealer Cost', 2000, 200000)

for col in [
    'Engine Size (l)', 'Cyl', 'Horsepower(HP)',
    'City Miles Per Gallon', 'Highway Miles Per Gallon',
    'Weight', 'Wheel Base', 'Len', 'Width',
    'Retail Price', 'Dealer Cost'
]:
    df[col] = df.groupby('Type')[col].transform(lambda x: x.fillna(x.median()))

df.to_csv("cars_information_cleaned.csv", index=False)
