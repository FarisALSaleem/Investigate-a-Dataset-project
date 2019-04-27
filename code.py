#!/usr/bin/env python3git
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta


def remove_nulls_and_duplicates(d):
    '''removes any nulls and duplicates it finds when given a dataframe'''
    if sum(d.duplicated()) > 0:
        d = d.drop_duplicates(inplace=True)
    if d.isnull().sum().any():
        d = d.dropna(inplace=True)
    # this part had to be hard coded becauses .isnull() does not detect negative numbers
    d.loc[(d.Age < 0), 'Age'] = round(df["Age"].mean())
    return d


def change_to_int64(d, fields):
    '''takes a dataframe and a list of fields and changes the type of those fields into np.int64'''
    for field in fields:
        d[field] = d[field].astype(np.int64)
    return d


def change_to_datetime64(d, fields):
    '''takes a dataframe and a list of fields and changes the type of those fields into datetime64[ns]'''
    for field in fields:
        d[field] = d[field].astype('datetime64[ns]')
    return d


def change_to_bool(d, fields):
    '''takes a dataframe and a list of fields and changes the type of those fields into 'bool'''
    for field in fields:
        d[field] = d[field].astype('bool')
    return d


if __name__ == '__main__':
    # step 1 load csv
    df = pd.read_csv('noshowappointments-kagglev2-may-2016.csv')
    # step 2 Data wrangling

    # step 2.1 Remove nulls & duplicates
    df = remove_nulls_and_duplicates(df)

    # step 2.2 Fix types
    df = change_to_int64(df, ['PatientId'])
    df = change_to_datetime64(df, ['ScheduledDay', 'AppointmentDay'])
    df = change_to_bool(df, ['Scholarship', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap', 'SMS_received'])
    # change the name of the No-show field into No_show becauses it's easier to deal with in .query()
    df['No_show'] = df['No-show'].replace(dict(Yes=True, No=False))
    del df['No-show']

    # step 3 Exploratory Data Analysis

    # step 3.1 is there a relationship between (AppointmentDay-ScheduledDay) & No-show
    df["Days_Between_Ad_Sd"] = df['AppointmentDay'].dt.date - df['ScheduledDay'].dt.date

    # plot 1 - "Relationship between (AppointmentDay - ScheduledDay)\n and patiences showing up" (not useful)
    plt.scatter(x=df["Days_Between_Ad_Sd"].astype('timedelta64[D]'), y=df['No_show'])
    plt.title("Relationship between (AppointmentDay - ScheduledDay)\n and patiences showing up")
    plt.xlabel("(AppointmentDay - ScheduledDay)")
    plt.ylabel("The number of patiences that show up")
    plt.show()

    # plot 2 - The % of Patients that showed up per group
    cutoffs = ['min', '25%', '50%', '75%', 'max']
    bin_names = ['Group_{}'.format(num) for num in range(len(cutoffs))[1:]]
    bin_edges = [timedelta(-7), timedelta(0), timedelta(4), timedelta(15), timedelta(179)]
    df['Days_Between_Ad_Sd_Age_group'] = pd.cut(df['Days_Between_Ad_Sd'], bin_edges, labels=bin_names)

    groupsize = [
        df.query("Days_Between_Ad_Sd_Age_group == '{}'".format(bin_name)).count().AppointmentDay
        for bin_name in bin_names]
    groupShow = [
        df.query("Days_Between_Ad_Sd_Age_group == '{}' and No_show == False".format(bin_name)).count().AppointmentDay
        for bin_name in bin_names]
    groupShowp = [round((x / y) * 100).astype(int) for x, y in zip(groupShow, groupsize)]

    y = groupShowp
    xlabels = ["{} ({})".format(name, cutoff) for name, cutoff in zip(bin_names, cutoffs[1:])]
    x = range(len(bin_names))
    plt.bar(x, y)
    plt.xticks(x, xlabels)
    plt.xlabel("The Groups")
    plt.ylabel("The % of Patients that showed up")
    plt.title("The % of Patient that showed up per group")
    plt.show()

    # step 3.2 is there a relationship between SMS_received & No-show
    show = df.query('No_show == False').count().AppointmentDay
    no_show = df.query('No_show == True').count().AppointmentDay
    SMS_received = df.query('SMS_received == True').count().AppointmentDay
    SMS_received_show = df.query('SMS_received == True and No_show == False').count().AppointmentDay
    SMS_received_noshow = df.query('SMS_received == True and No_show == True').count().AppointmentDay
    noSMS_received = df.query('SMS_received == False').count().AppointmentDay
    noSMS_received_show = df.query('SMS_received == False and No_show == False').count().AppointmentDay
    noSMS_received_noshow = df.query('SMS_received == False and No_show == True').count().AppointmentDay

    # plot one - % of Patients that received a SMS & showed up Vs received a SMS & didn't show up
    y = [SMS_received_show / SMS_received, SMS_received_noshow / SMS_received]
    xlabels = ['Received SMS and showed up', "Received SMS but didn't showed up"]
    x = [1, 2]
    plt.bar(x, y)
    plt.xticks(x, xlabels)
    plt.title("% of Patient that received a SMS & showed up\nVs received a SMS & but didn't show up")
    plt.ylabel("% out of 1")
    plt.show()

    # plot two - % of Patients that didn't received a SMS but showed up Vs didn't received a SMS & didn't show up
    y = [noSMS_received_show / noSMS_received, noSMS_received_noshow / noSMS_received]
    xlabels = ["Didn't received SMS\nbut showed up", "Didn't received SMS\nand didn't showed up"]
    x = [1, 2]
    plt.bar(x, y)
    plt.xticks(x, xlabels)
    plt.title("% of Patient that didn't received a SMS but showed up\nVs didn't received a SMS & didn't show up")
    plt.ylabel("% out of 1")
    plt.show()

    # plot three -  % of Patients that received a SMS and showed up Vs didn't received a SMS but showed up
    y = [SMS_received_show / show, noSMS_received_show / show]
    xlabels = ['Received SMS and showed up', "Didn't received SMS\nbut showed up"]
    x = [1, 2]
    plt.bar(x, y)
    plt.xticks(x, xlabels)
    plt.title("% of Patients that received a SMS and showed up\nVs didn't received a SMS but showed up")
    plt.ylabel("% out of 1")
    plt.show()

    # plot four - % of Patiences that received a SMS but didn't show up Vs didn't received a SMS & didn't show up
    y = [SMS_received_noshow / no_show, noSMS_received_noshow / no_show]
    xlabels = ["Received SMS but didn't showed up", "Didn't received SMS\nand didn't showed up"]
    x = [1, 2]
    plt.bar(x, y)
    plt.xticks(x, xlabels)
    plt.title("% of Patients that received a SMS but didn't show up\nVs didn't received a SMS & didn't show up")
    plt.ylabel("% out of 1")
    plt.show()

    # step 3.3 is there relationship between age & no-show
    # plot one - The % of patients that showed up per group
    cutoffs = ['min', '25%', '50%', '75%', 'max']
    bin_names = ['Group_{}'.format(num) for num in range(len(cutoffs))[1:]]
    bin_edges = [np.NINF, 18, 37, 55, 115]
    df['Age_group'] = pd.cut(df['Age'], bin_edges, labels=bin_names)

    groupsize = [df.query("Age_group == '{}'".format(bin_name)).count().AppointmentDay for bin_name in bin_names]
    groupShow = [df.query("Age_group == '{}' and No_show == False".format(bin_name)).count().AppointmentDay for
                 bin_name in bin_names]
    groupShowp = [round((x / y) * 100).astype(int) for x, y in zip(groupShow, groupsize)]

    y = groupShowp
    xlabels = ["{} ({})".format(name, cutoff) for name, cutoff in zip(bin_names, cutoffs[1:])]
    x = range(len(bin_names))
    plt.bar(x, y)
    plt.xticks(x, xlabels)
    plt.title("Age group show %")
    plt.xlabel("The Groups")
    plt.ylabel("The % of patients that showed up")
    plt.title("The % of patients that showed up per group")
    plt.show()
