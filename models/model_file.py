import numpy as np
import pandas as pd

def discretize(curr_card, curr_traded_card, trades_before, players_after):
    """
    convert the situation to a single integer
    """
    return curr_card * 1500 + curr_traded_card * 100 + trades_before * 10 + players_after * 1

def understand_data(np_file):
    data = np.load(np_file)
    # Get the index of the array
    index = np.arange(len(data))
    # Create the dataframe
    df = pd.DataFrame(data, index=index)
    # Save the dataframe to CSV
    df['curr_card'] = index // 1500
    df['curr_traded_card'] = (index % 1500) // 100
    df['trades_before'] = (index % 100) // 10
    df['players_after'] = index % 10
    df.rename(columns={0:'Trade', 1:'Stay'}, inplace=True)
    print(df.tail())

    df.to_csv('./model2.csv')



if __name__ == "__main__":
    understand_data('./model2.npy')