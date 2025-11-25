#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Clean and fix cars.csv, output to cars_cleaned.csv
#
# Proper handling of real anomalies in this dataset:
# - City MPG = 1000 → normalized by dividing by 100 to become 10
# - Width = 2, Wheel Base = 0, Engine Size = 0, Cyl = 0, etc.
#   are filled using the median or mode of the same vehicle type group


import pandas as pd
import numpy as np
from pathlib import Path

INFILE = "cars.csv"
OUTFILE = "cars_cleaned.csv"

def main():
    df = pd.read_csv(INFILE)

   
    for c in ['Name', 'Type']:
        df[c] = df[c].astype(str).str.strip()

    num_cols = [
        'AWD', 'RWD', 'price_retail', 'price_dealer', 'Engine Size (l)', 'Cyl', 'Horsepower(HP)',
        'City Miles Per Gallon', 'Highway Miles Per Gallon', 'Weight', 'Wheel Base', 'Len', 'Width'
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    
    def derive_drive(row):
        if row.get('AWD', 0) == 1: return 'AWD'
        if row.get('RWD', 0) == 1: return 'RWD'
        return 'FWD/Other'
    df['drive'] = df.apply(derive_drive, axis=1)

   
    med_by_type = df.groupby('Type').median(numeric_only=True)

    # ---fix outliers/anomalies---
    fixes = {}

    # 1) City MPG > 100
    mask = df['City Miles Per Gallon'] > 100
    fixes['City Miles Per Gallon_gt100'] = int(mask.sum())
    df.loc[mask, 'City Miles Per Gallon'] = df.loc[mask, 'City Miles Per Gallon'] / 100.0  # 1000 -> 10

    # 2) Width < 50
    mask = df['Width'] < 50
    fixes['Width_lt50'] = int(mask.sum())
    if fixes['Width_lt50'] > 0:
        df.loc[mask, 'Width'] = df.loc[mask].apply(
            lambda r: med_by_type.loc[r['Type'], 'Width'], axis=1
        )

    # 3) Wheel Base <= 50
    mask = df['Wheel Base'] <= 50
    fixes['Wheel Base_le50'] = int(mask.sum())
    if fixes['Wheel Base_le50'] > 0:
        df.loc[mask, 'Wheel Base'] = df.loc[mask].apply(
            lambda r: med_by_type.loc[r['Type'], 'Wheel Base'], axis=1
        )

    # 4) Engine Size <= 0
    mask = df['Engine Size (l)'] <= 0
    fixes['Engine Size (l)_le0'] = int(mask.sum())
    if fixes['Engine Size (l)_le0'] > 0:
        df.loc[mask, 'Engine Size (l)'] = df.loc[mask].apply(
            lambda r: med_by_type.loc[r['Type'], 'Engine Size (l)'], axis=1
        )

    # 5) Cyl <= 0
    mask = df['Cyl'] <= 0
    fixes['Cyl_le0'] = int(mask.sum())
    if fixes['Cyl_le0'] > 0:
        mode_by_type = df.groupby('Type')['Cyl'].agg(lambda s: s.mode().iloc[0])
        df.loc[mask, 'Cyl'] = df.loc[mask, 'Type'].map(mode_by_type).astype(int)

    # 6) Highway Miles Per Gallon Outliers(<5 or >80 or NaN)
    mask = (df['Highway Miles Per Gallon'] < 5) | (df['Highway Miles Per Gallon'] > 80) | (df['Highway Miles Per Gallon'].isna())
    fixes['Highway Miles Per Gallon_outlier'] = int(mask.sum())
    if fixes['Highway Miles Per Gallon_outlier'] > 0:
        df.loc[mask, 'Highway Miles Per Gallon'] = df.loc[mask].apply(
            lambda r: med_by_type.loc[r['Type'], 'Highway Miles Per Gallon'], axis=1
        )
        
    # --- Remove duplicates (by vehicle model name)---
    before = len(df)
    df = df.drop_duplicates(subset=['Name'])
    fixes['drop_duplicates'] = before - len(df)

    # ---Outfile---
    df.to_csv(OUTFILE, index=False)

    # ---Report ---
    print(f"Saved: {OUTFILE}")
    for k, v in fixes.items():
        print(f"{k}: {v}")

    # --- Sanity Check ---
    debug_names = [
        "Infiniti FX45",
        "Audi A6 3.0 Quattro 4dr",
        "Buick Park Avenue 4dr",
        "Audi A4 3.0 Quattro 4dr auto",
        "Audi A4 3.0 4dr",
    ]
    sample = df[df['Name'].isin(debug_names)][
        ['Name','City Miles Per Gallon','Highway Miles Per Gallon','Width','Wheel Base','Engine Size (l)','Cyl']
    ]
    if not sample.empty:
        print("\nSanity check (key fixed rows):")
        print(sample.to_string(index=False))

if __name__ == "__main__":
    assert Path(INFILE).exists(), f"Input file {INFILE} not found."
    main()
