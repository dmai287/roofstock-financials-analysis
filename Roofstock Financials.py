#!/usr/bin/env python
# coding: utf-8



import warnings
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

warnings.filterwarnings("ignore")


matched_chicago = pd.read_csv('matched_chicago.csv')

illinois_utilities = 376.80
capex_rate = 0.04
matched_chicago['capex_r'] = matched_chicago['sold_price'] * capex_rate



# Gross Yield
matched_chicago['gross_yield'] = ((matched_chicago['listing_amount'] * 12) /
                                  matched_chicago['sold_price']) * 100

new_matched_chicago = matched_chicago.dropna(subset=['gross_yield'])


median_squarefeet_chicago = matched_chicago['square_feet'].median() 
chicago_utilities_per_sf = illinois_utilities / median_squarefeet_chicago

# Utilities
new_matched_chicago['utilities'] = chicago_utilities_per_sf * new_matched_chicago['square_feet']

# Insurance 
new_matched_chicago['insurance'] = (new_matched_chicago['sold_price'] / 1000 ) * 3.5

# Repairs & Maint
repairs = 0.02
new_matched_chicago['repairs_and_maint'] = new_matched_chicago['sold_price'] * repairs

# Property Management
management = 0.03
new_matched_chicago['management'] = new_matched_chicago['sold_price'] * management

# Expense 
new_matched_chicago['expense'] = new_matched_chicago['management'] +     new_matched_chicago['repairs_and_maint'] +     new_matched_chicago['insurance'] + new_matched_chicago['utilities']

# Vaccancy at 5%
vacancy = 0.05
new_matched_chicago['income'] = (new_matched_chicago['listing_amount'] * (1 - vacancy)) * 12

# Net Operating Income 
new_matched_chicago['net_operating_income_year1'] = new_matched_chicago['income'] - new_matched_chicago['expense']

# Total Unlevered Cash Flow
new_matched_chicago['total_unlevered_cash_flow_y1'] = new_matched_chicago['net_operating_income_year1'] - new_matched_chicago['capex_r']

# Mortgage

# Mortgage Rate (replace this with API)
loan_interest_rate = 7 /100

# Down Payment (default)
down_payment = 20 /100

# Loan Term & Number of payment per year (default)
loan_term = 30 
number_of_payment_per_year = 12

# Monthly Payment Amount
def monthly_payment(purchase_price, down_payment, current_mortgage_rate, number_of_payment_per_year):
    starting_loan_amount = purchase_price - (purchase_price * down_payment)
    loan_interest_rate = current_mortgage_rate
    number_of_payment_per_year = number_of_payment_per_year
    monthly_payment = (starting_loan_amount *
                       (loan_interest_rate / number_of_payment_per_year)) / (
                           1 -
                           (1 +
                            (loan_interest_rate / number_of_payment_per_year)) **
                           (-(loan_term * number_of_payment_per_year)))
    return monthly_payment

new_matched_chicago['monthly_payment'] = monthly_payment(new_matched_chicago['sold_price'], down_payment, loan_interest_rate, number_of_payment_per_year)
new_matched_chicago['mortgage'] = new_matched_chicago['monthly_payment'] * 12


# Total Net Cash Flow
new_matched_chicago['net_cf_year1'] = new_matched_chicago['total_unlevered_cash_flow_y1'] -     new_matched_chicago['mortgage']


# Cash-on-Cash
new_matched_chicago['cash_on_cash'] = (new_matched_chicago['net_cf_year1'] /     new_matched_chicago['sold_price']) * 100


# Cap Rate
new_matched_chicago['cap_rate'] = (
    new_matched_chicago['net_operating_income_year1'] /
    new_matched_chicago['sold_price']) * 100


# Initial Investment
immediate_repair = 0.01  # <- default
closing_cost = 1.5 /100

new_matched_chicago['immediate_repair_cost'] = new_matched_chicago['sold_price'] * immediate_repair

new_matched_chicago['loan_fee'] = new_matched_chicago['sold_price'] *     (0.75/100)

new_matched_chicago['initial_investment'] = (down_payment * new_matched_chicago['sold_price']) +     (closing_cost * new_matched_chicago['sold_price']) +     new_matched_chicago['immediate_repair_cost'] +     new_matched_chicago['loan_fee']


# Total Return

# Loan Balance
remain_year = 30 - 1

new_matched_chicago['loan_balance'] = (
    new_matched_chicago['monthly_payment'] *
    (1 - (1 + (loan_interest_rate / number_of_payment_per_year))**
     (-(remain_year * number_of_payment_per_year)))) / (
         loan_interest_rate / number_of_payment_per_year)

# Disposition Fee
new_matched_chicago['disposition_fee'] = new_matched_chicago['sold_price'] * (
    3.5 / 100)

# Sale Proceed
new_matched_chicago[
    'sale_proceed'] = new_matched_chicago['sold_price'] - new_matched_chicago[
        'loan_balance'] - new_matched_chicago['disposition_fee']

# Total Return
new_matched_chicago['total_return_y1'] = new_matched_chicago[
    'sale_proceed'] + new_matched_chicago[
        'net_cf_year1'] - new_matched_chicago['initial_investment']

# Annualized Return Year 1
new_matched_chicago['annualized_return_y1'] = (
    ((new_matched_chicago['initial_investment'] / new_matched_chicago['total_return_y1'])**
     (1 / 1)) - 1) * 100



year_forward = 5
rent_growth = 0.05
appreciation = 0.05

remain_year = loan_term - year_forward

# Loan Balance Year 5
new_matched_chicago['loan_balance_y5'] = (
    new_matched_chicago['monthly_payment'] *
    (1 - (1 + (loan_interest_rate / number_of_payment_per_year))**
     (-(remain_year * number_of_payment_per_year)))) / (
         loan_interest_rate / number_of_payment_per_year)

# Income Year 5
new_matched_chicago['income_y5'] = new_matched_chicago['income'] * (
    1 + rent_growth)**year_forward

# NOI Year 5:
new_matched_chicago['noi_y5'] = new_matched_chicago[
    'income_y5'] - new_matched_chicago['expense']

# Total Unlevered Cash Flow Year 5:
new_matched_chicago['total_unlevered_cash_flow_y5'] = new_matched_chicago[
    'noi_y5'] - new_matched_chicago['capex_r']

# Paid Loan Amount Year 5:
new_matched_chicago['paid_loan_amount_y5'] = new_matched_chicago[
    'monthly_payment'] * (12 * year_forward)

# Total Net Cash Flow Year 5:
new_matched_chicago['total_net_cash_flow_y5'] = new_matched_chicago[
    'total_unlevered_cash_flow_y5'] - new_matched_chicago['paid_loan_amount_y5']

# Property Value Year 5:
new_matched_chicago['property_value_y5'] = new_matched_chicago[
    'sold_price'] * (1 + appreciation)**year_forward

# Sale Proceed Year 5:
new_matched_chicago['sale_proceed_y5'] = new_matched_chicago[
    'property_value_y5'] - new_matched_chicago[
        'loan_balance_y5'] - new_matched_chicago['disposition_fee']

# Total Return Year 5:
new_matched_chicago['total_return_y5'] = new_matched_chicago[
    'sale_proceed_y5'] + new_matched_chicago[
        'total_net_cash_flow_y5'] - new_matched_chicago['initial_investment']

# Annualized Return Year 5: 
new_matched_chicago['annualized_return_y5'] = (
    ((new_matched_chicago['initial_investment'] / new_matched_chicago['total_return_y5'])**
     (1 / year_forward)) - 1) * 100


mycols = [
    'building_name', 'address_zip', 'bedrooms', 'full_baths', 'half_baths', 'square_feet', 'year_built', 'sold_price', 'income', 'expense', 'gross_yield',
    'cap_rate', 'cash_on_cash', 'annualized_return_y1', 'annualized_return_y5'
]



df = new_matched_chicago[mycols]
# df = df.dropna(subset=['cap_rate'])
# df.replace([np.inf, -np.inf], np.nan, inplace=True)
# df.dropna(subset=["cap_rate"], how="all", inplace=True)

df





