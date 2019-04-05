import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt


def remove_nulls_and_duplicates(df):
    if sum(df.duplicated()) > 0:
        df = df.drop_duplicates(inplace=True)
    if not df.isnull().sum().any():
        df = df.dropna(inplace=True)
    return df


def change_to_int64(df, fields):
    for field in fields:
        df[field] = df[field].astype(np.int64)
    return df


def change_to_datetime64(df, fields):
    for field in fields:
        df[field] = df[field].astype('datetime64[ns]')
    return df


def change_to_bool(df, fields):
    for field in fields:
        df[field] = df[field].astype('bool')
    return df


if __name__ == '__main__':
    # step 1 load csv
    df = pd.read_csv('noshowappointments-kagglev2-may-2016.csv')

    # step 2 data wrangling

    # step 2.1 remove nulls & duplicates
    df = remove_nulls_and_duplicates(df)

    # step 2.2 fix types
    df = change_to_int64(df, ['PatientId'])
    df = change_to_datetime64(df, ['ScheduledDay', 'AppointmentDay'])
    df = change_to_bool(df, ['Scholarship', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap', 'SMS_received'])
    df['No-show'] = df['No-show'].replace(dict(Yes=1, No=0))
    
    # step 2.3 clean the Strings in the Neighbourhood field






