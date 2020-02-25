from MisItemHandler import getfrommisitem;
from MismatchHandler import get_from_mismatch;
import pandas as pd;

def fetch_product_specified(input_df):
    
    misitem_output_pd = pd.DataFrame();

    for j in range(len(input_df.index)):
#        print j;
        misitem_output_pd = misitem_output_pd.append(getfrommisitem(input_df.ix[[j]]),ignore_index=True); 
    misitem_output_pd.index = input_df.index;

    mismatch_output_pd = pd.DataFrame();

    for j in range(len(input_df.index)):
#       print j;
        mismatch_output_pd = mismatch_output_pd.append(get_from_mismatch(input_df.ix[[j]]),ignore_index=True); 
    mismatch_output_pd.index = input_df.index;

#    print misitem_output_pd;
#    print mismatch_output_pd;

    result = pd.concat([misitem_output_pd, mismatch_output_pd], axis=1);
#    print result;
#    print input_df.columns
    return result;