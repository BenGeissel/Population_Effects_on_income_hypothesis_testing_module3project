import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import math
import scipy.stats as st

def census_api_data_cleaner():
    '''
    Function to request API Data for population by county.
    
    Input: None.
    
    Output: Cleaned pandas dataframe with population data by FIPS code.
    '''
    
    #US Census Bureau API Key and Request. Show if request is bad.
    api_key = 'b75abaaeb7e41a94fca6dce80b3eeac5289e46a9'
    resp = requests.get(f'http://api.census.gov/data/2018/pep/population?get=POP&for=county:*&key={api_key}')
    if resp.status_code != 200:
        print("Error! Help me!")
    
    #Format data in json and convert to pandas dataframe.
    poplist = resp.json()
    pop_df = pd.DataFrame(poplist[1:], columns = poplist[0])
    
    #Create FIPS data.
    pop_df['FIPS'] = pop_df.state + pop_df.county
    
    #Change population data to integer from string.
    pop_df.POP = pop_df.POP.astype('int')
    
    #Remove unwanted columns.
    del pop_df['state']
    del pop_df['county']
    
    return pop_df


def rural_county_info_cleaner(excel_file):
    '''
    Function to clean Excel data for rural county information.
    
    Input: Excel file path.
    
    Output: Cleaned pandas dataframe with county rural information.
    '''
    
    #Read in Excel file. Skip first 3 rows to get to data table.
    rural_lookup = pd.read_excel(excel_file, skiprows = 3)
    
    #Drop unnecessary rows and columns.
    rural_lookup.drop(rural_lookup.tail(6).index,inplace=True)
    del rural_lookup['Note']
    del rural_lookup['Unnamed: 8']
    
    #Rename columns for easier use.
    rural_lookup.columns = ['FIPS', 'State', 'County_State', 'Total_pop', 'Urban_pop', 'Rural_pop', 'Percent_Rural']
    
    return rural_lookup

def rural_marker(percent):
    '''
    Function to bin county populations into 3 categories.
    
    Input: County rural population percentage.
    
    Output: County population category.
    '''
    
    marker = None
    if percent <= 30:
        marker = 'Urban'
    elif percent <= 70:
        marker = 'Mix/Suburban'
    else:
        marker = 'Rural'
        
    return marker


def classify_county_populations(df1, df2):
    '''
    Function to merge county population data with rural information data and bin into categories.
    
    Input: County population dataframe and rural information dataframe.
    
    Output: Merged and binned county population dataframe.
    '''
    
    #Merge dataframes.
    pop_df1 = df1.merge(df2[['FIPS', 'County_State', 'Percent_Rural']], on = 'FIPS', how = 'inner')
    
    #Bin in to population categories based on rural percentage.
    pop_df1['pop_category'] = pop_df1.Percent_Rural.map(lambda x: rural_marker(x))
    
    return pop_df1

def income_unemployment_cleaner(csv_file):
    ''' 
    Function to clean income and unemployment data, remove currency symbol, comma, convert string to int 
   
    Input: median income and unemployment dataset
    
    Output: cleaned dataset by FIPS code 
    '''

    df = pd.read_csv(csv_file)
    df_2017 = df[['FIPS',"State","Area_name","Unemployment_rate_2017","Median_Household_Income_2017"]]
    
    # 
    df_2017 = df_2017.dropna()
    df_2017['Median_Household_Income_2017'] = df_2017.Median_Household_Income_2017.apply(lambda x: x.replace('$',''))
    df_2017['Median_Household_Income_2017'] = [col.replace(',', '') for col in df_2017.Median_Household_Income_2017]
    df_2017['Median_Household_Income_2017'] = df_2017['Median_Household_Income_2017'].astype("int")
    df_2017['Unemployment_rate_2017'] = df_2017['Unemployment_rate_2017'].astype("float")
    df_2017['FIPS'] = df_2017['FIPS'].apply(lambda x: "{0:0=5d}".format(x))
    
    return df_2017
    
    
def calculate_means_stds(df):
    '''
    Function to calculate means and standard deviations for a dataframe for both unemployment and median income.
    
    Input: Dataframe.
    
    Output: Income mean, Income standard deviation, Unemployment mean, Unemployment standard deviation.
    '''
    
    income_mean = df.Median_Household_Income_2017.mean()
    income_std = df.Median_Household_Income_2017.std()
    UE_mean = df.Unemployment_rate_2017.mean()
    UE_std = df.Unemployment_rate_2017.std()
    
    return income_mean, income_std, UE_mean, UE_std


def z_test(x_bar, mu, sigma):
    '''
    Function to calculate z-statistic and p-value.
    
    Input: x_bar, mu, sigma.
    
    Output: Z-statistic and P-value.
    '''
    
    z = (x_bar - mu)/(sigma)
    p = 1 - st.norm.cdf(z)
    
    return z, p


def hypothesis(p_value):
    '''
    Function to evaluate p-value to reject or fail to reject null hypothesis.
    
    Input: P-value.
    
    Output: Print statement evaluation.
    '''
    
    alpha = .05
    if p_value < alpha:
        print('Reject Null Hypothesis')
    else:
        print('Fail to Reject Null Hypothesis')