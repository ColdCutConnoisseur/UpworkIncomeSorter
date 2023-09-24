"""Utility script for sorting UpWork jobs/income for quarterly/annual tax purposes"""

import sys
import csv
import datetime
import calendar

import pandas as pd

# TODO: REMOVE 'PENDING' TRANSACTIONS FROM SUMMARIES
# INFO: Above relates to not wanting to pay taxes on income not yet received in account


class UpWorkTransactionTypes:
    MEMBERSHIP_FEE = "Membership Fee"
    SERVICE_FEE = "Service Fee"
    BONUS = "Bonus"
    FIXED_PRICE = "Fixed Price"
    REFUND = "Refund"
    HOURLY = "Hourly"
    WITHDRAWAL = "Withdrawal"
    MISCELLANEOUS = "Miscellaneous"

class QuarterCodes:
    q1 = {'name': 'q1', 'start_month': 1,  'end_month': 3} 
    q2 = {'name': 'q2', 'start_month': 4,  'end_month': 6}
    q3 = {'name': 'q3', 'start_month': 7,  'end_month': 9}
    q4 = {'name': 'q4', 'start_month': 10, 'end_month': 12}

def return_frame_for_year(tax_year, full_frame):
    begin_date = datetime.datetime(day=1, month=1, year=tax_year)
    filtered_frame = full_frame[full_frame.Date >= begin_date]
    return filtered_frame

def produce_annual_summary(income_transactions, cost_transactions, withdrawal_transactions):
    print("ANNUAL SUMMARY:")
    total_income = sum([txn.Amount for txn in income_transactions])
    print(f"Total Income: {total_income}")

    total_costs = sum([txn.Amount for txn in cost_transactions])
    print(f"Total Costs: {total_costs}")

    print(f"Net: {total_income + total_costs:.2f}")

    total_withdrawals = sum([txn.Amount for txn in withdrawal_transactions])
    print(f"Total Withdrawals: {total_withdrawals}")

    print('\n')

def summarize_for_quarter(quarter_months_dict, tax_year, income_transactions,
            cost_transactions, withdrawal_transactions):
    """Use 'tax_year' for assertion is correct tax year"""
    print(f"[{quarter_months_dict['name'].upper()} Summary]")

    #Set ranges
    quarter_begin_date = datetime.datetime(day=1, month=quarter_months_dict['start_month'], year=tax_year) 
    
    end_month = quarter_months_dict['end_month']
    end_month_monthrange = calendar.monthrange(tax_year, end_month)
    last_day_in_month = end_month_monthrange[1]
    #print(f"DEBUG: Last day in month {end_month} --> {last_day_in_month}")
    quarter_end_date = datetime.datetime(day=last_day_in_month, month=end_month, year=tax_year)
    
    #Filter
    income_transactions_for_quarter = [txn for txn in income_transactions if 
                                          (txn.Date >= quarter_begin_date) and
                                          (txn.Date <= quarter_end_date)]

    cost_transactions_for_quarter = [txn for txn in cost_transactions if
                                        (txn.Date >= quarter_begin_date) and
                                        (txn.Date <= quarter_end_date)]

    withdrawal_transactions_for_quarter = [txn for txn in withdrawal_transactions if
                                              (txn.Date >= quarter_begin_date) and
                                              (txn.Date <= quarter_end_date)]

    #Amount Summaries
    total_quarterly_income = sum([txn.Amount for txn in income_transactions_for_quarter])
    print(f"\tTotal Quarterly Income: {total_quarterly_income}")

    total_quarterly_costs = sum([txn.Amount for txn in cost_transactions_for_quarter])
    print(f"\tTotal Quarterly Cost: {total_quarterly_costs}")

    total_quarterly_withdrawals = sum([txn.Amount for txn in withdrawal_transactions_for_quarter])
    print(f"\tTotal Quarterly Withdrawals: {total_quarterly_withdrawals}")

    print(f"\t---------------------------------------------------")

    total_quarterly_net = total_quarterly_income + total_quarterly_costs
    print(f"\tTotal Quarterly Net: {total_quarterly_net:.2f}")

    print('\n')
    print('\n')


def sort_transaction_data(transaction_file_path, tax_year):
    print(f"UpWork Freelance Income [TAX_YEAR: {tax_year}]_______________________________________________")
    transaction_dataframe = pd.read_csv(transaction_file_path, parse_dates=[0])
    transaction_dataframe.sort_values(by=['Date'], ascending=True, inplace=True, ignore_index=True)

    #Returns frame with transaction_date > Jan1 of tax_year
    #NOTE: Use end_date to clip off 'pending' transactions (temporary) (SEE note at top)
    #end_date = datetime.datetime()
    this_years_transactions = return_frame_for_year(tax_year, transaction_dataframe)

    income_transactions = []
    cost_transactions = []
    withdrawal_transactions = []
    
    #Classify transactions
    for txn in this_years_transactions.itertuples(index=False, name="UpWorkTransaction"):

        txn_type = txn.Type

        #Txn cases
        if txn_type == UpWorkTransactionTypes.MEMBERSHIP_FEE:
            #print(f"{UpWorkTransactionTypes.MEMBERSHIP_FEE} UpWork Transaction Type recognized")
            cost_transactions.append(txn)

        elif txn_type == UpWorkTransactionTypes.SERVICE_FEE:
            #print(f"{UpWorkTransactionTypes.SERVICE_FEE} UpWork Transaction Type recognized")
            cost_transactions.append(txn)

        elif txn_type == UpWorkTransactionTypes.BONUS:
            #print(f"{UpWorkTransactionTypes.BONUS} UpWork Transaction Type recognized")
            income_transactions.append(txn)

        elif txn_type == UpWorkTransactionTypes.FIXED_PRICE:
            #print(f"{UpWorkTransactionTypes.FIXED_PRICE} UpWork Transaction Type recognized")
            income_transactions.append(txn)

        elif txn_type == UpWorkTransactionTypes.REFUND:
            #print(f"{UpWorkTransactionTypes.REFUND} UpWork Transaction Type recognized")
            cost_transactions.append(txn)

        elif txn_type == UpWorkTransactionTypes.HOURLY:
            #print(f"{UpWorkTransactionTypes.HOURLY} UpWork Transaction Type recognized")
            income_transactions.append(txn)

        elif txn_type == UpWorkTransactionTypes.WITHDRAWAL:
            #print(f"{UpWorkTransactionTypes.WITHDRAWAL} UpWork Transaction Type recognized")
            withdrawal_transactions.append(txn)

        elif txn_type == UpWorkTransactionTypes.MISCELLANEOUS:
            #print(txn)
            #sys.exit(0)
            income_transactions.append(txn)

        else:
            print(f"Unhandled UpWork Transaction Type: {txn_type}")
            print("NOTE: Please add unhandled transaction type to repository / issues!")
            print("Exiting...")
            sys.exit(0)

    #print("INCOME")
    #print(income_transactions)
    #print('\n')
    #print("COSTS")
    #print(cost_transactions)
    #print('\n')
    #print("WITHDRAWALS")
    #print(withdrawal_transactions)

    produce_annual_summary(income_transactions, cost_transactions, withdrawal_transactions)

    summarize_for_quarter(QuarterCodes.q1, tax_year, income_transactions, cost_transactions, withdrawal_transactions)
    summarize_for_quarter(QuarterCodes.q2, tax_year, income_transactions, cost_transactions, withdrawal_transactions)
    summarize_for_quarter(QuarterCodes.q3, tax_year, income_transactions, cost_transactions, withdrawal_transactions)
    summarize_for_quarter(QuarterCodes.q4, tax_year, income_transactions, cost_transactions, withdrawal_transactions)


if __name__ == "__main__":
    TRANSACTION_FILE_PATH = "./sample_upwork_transactions.csv"
    TAX_YEAR = 2023

    sort_transaction_data(TRANSACTION_FILE_PATH, TAX_YEAR)
