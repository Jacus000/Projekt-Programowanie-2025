import pandas as pd
import re


### standaryzcja tekstu

def clear(value):
    if pd.isnull(value):
        return value
    value = str(value).lower()
    value = re.sub(r"[^a-z0-9]", "", value)
    return value


def unify_text(data):
    data_c = data.copy()
    text_column = data_c.select_dtypes(include=["object", "string"]).columns
    for column in text_column:
        data_c[column] = data_c[column].apply(clear)
    return data_c

###
##zamiana tekst na wartosci
def change_to_value(df, column, name_value=None):

    if column not in df.columns:
        raise ValueError(f"Kolumna '{column}' nie istnieje w DataFrame.")

    if name_value is None:
        name_value = column + "_value"

    df[name_value] = pd.factorize(df[column])[0]
    return df


#usuwa wiersze z nan
def remove_nan(df):
    return df.dropna()


def nan_count(df):
    return df.isnull().sum().sum()

#zamien nan na x
def fill_nan(df, x):
    return df.fillna(x)

#usuwa kolumne z liczba nan > x
def remove_if_x_nan(df, x):
    return df.loc[:, df.isnull().mean() < x]


#liczba unikalnych
def count_unique_in_col(df):
    return df["kolumna"].nunique()



#usuwa duplikaty wiersze
def usun_duplikaty(df):
    return df.drop_duplicates()

#usuwa wiersze tam gdzie jest same nan
def delete_nan_row(df):
    return df.dropna(how="all")



#zamienia Nan na srednia
def change_nan_to_mean(dane):
    dane_kopia = dane.copy()

    for kolumna in dane_kopia.select_dtypes(include="number").columns:
        if dane_kopia[kolumna].isnull().any():
            srednia = dane_kopia[kolumna].mean()
            dane_kopia[kolumna] = dane_kopia[kolumna].fillna(srednia)

    return dane_kopia