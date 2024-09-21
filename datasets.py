
import os
import pandas as pd

# Returns all files in the provided directory
def return_items(directory_path: str) -> list:
    all_items = {}
    # Check if provided path is a directory
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"{directory_path} is not a valid directory")
    
    # List all itens in the directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    dirs = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
    all_items = {'Files': files,
                 'Directories': dirs}
    
    return all_items

# Reads one [xls, xlsx, csv] file and returns it as a dataframe object
def return_dataset(file_path: str) -> object:
    # Check if file path exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Read Excel file
    if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            raise ValueError(f"Error reading Exce l file: {e}")
    
    # Read CSV file
    elif file_path.endswith('.csv'):
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
    else:
        raise ValueError(f"File format not supported")
    
    return df

# Creation and Transformation of Orders Dataset
def create_orders_dataset(dataset: object) -> object:
    df = dataset.copy()
    df['Cost'] = df['Sales'] - df['Profit']
    df['Unit_Cost'] = df['Cost'] / df['Quantity']
    # df['Market_Basket'] = df.groupby('Order ID')['Product ID'].transform(lambda x: ' + '.join(x))

    # df['Market_Basket'] = df.groupby('Order ID')['Product ID'].transform(lambda x: list(x))

    df_basket = df.groupby('Order ID')['Product ID'].agg(list).reset_index()
    df = df.merge(df_basket, on='Order ID', suffixes=('', '_Market_Basket'))
    df.rename(columns={
        'Product ID_Market_Basket': 'Market_Basket'
    }, inplace=True)
    df['Market_Basket'] = df['Market_Basket'].apply(tuple)
    # Convert Market_Basket to tuples and calculate frequencies
    frequency = df['Market_Basket'].value_counts()
    # Map the frequencies back to the original DataFrame
    df['Frequency'] = df['Market_Basket'].map(frequency)

    return df

# Creation and Transformation of Market Basket Dataset
def create_market_basket(dataset: object) -> object:
    df = dataset.copy()
    df = df.groupby('Market_Basket').agg({
        'Sales': 'sum',
        'Cost': 'sum',
        'Profit': 'sum',
        'Frequency': 'first'
        }).reset_index()
    # Rename columns
    df.rename(columns={
        'Sales': 'Total_Sales',
        'Cost': 'Total_Cost',
        'Profit': 'Total_Profit'
        }, inplace=True)
    # Create new columns
    df['Profit_percent'] = (df['Total_Profit'] / df['Total_Sales']) * 100
    df['Avg_Transaction'] = df['Total_Sales'] / df['Frequency']
    # Rename Index
    df = df.reset_index().rename(columns= {'index': 'id'})

    return df

# Create Products Dataset
def create_product_dataset(dataset: object) -> object:
    df = dataset.copy()
    # Group by ProductID and sum the Sales
    df = df.groupby('Product ID', as_index=False).agg({
        'Sales': 'sum',
        'Profit': 'sum'
        }).reset_index()
    # Rename columns
    df.rename(columns={
        'Sales': 'Total_Sales',
        'Profit': 'Total_Profit'
    }, inplace=True)
    # Create new column
    df['Profit_percent'] = (df['Total_Profit'] / df['Total_Sales']) * 100

    return df

# List all files in diretory
path = os.getcwd() + '/data/'
filename = 'Order-Data.xlsx'
# print(return_items(path))

df = return_dataset(path+filename)

# Create Orders DataFrame
orders_df = create_orders_dataset(df)
# Create Market Basket DataFrame
market_basket_df = create_market_basket(orders_df)
# Create Products DataFrame
products_df = create_product_dataset(df)



def print_details(order_id=None, product_id=None):
    print(market_basket_df[market_basket_df['Market_Basket'].str.contains(product_id)])
    print(products_df[products_df['Product ID'] == product_id])
    print(orders_df[orders_df['Product ID'] == product_id].drop(orders_df.columns[[2,3,4,5,6,7,8,9,10,12,13,14,21,22]], axis=1))

# print_details(product_id='FUR-CH-10000454')
print(orders_df)
    # print local variables
    # print(locals())

    # Orders file
    # filename = 'Order-Data.xlsx'
    # fpath = os.path.join(os.getcwd(), 'data/')

    # excel_file = pd.ExcelFile(fpath + filename)
    # # print(excel_file.sheet_names)


    # dfs = {}
    # for sheet_name in excel_file.sheet_names:
    #     modified_name = f"{sheet_name}_df"
    #     dfs[modified_name] = pd.read_excel(fpath + filename, sheet_name=sheet_name)

    # df = dfs['df'].copy()




