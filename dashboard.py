import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import datasets


# Load dataset
df = datasets.orders_df
products = datasets.products_df
market_basket = datasets.create_market_basket(df)

# Initialize Dash app
app = dash.Dash(__name__)

# App Layout Setup
app.layout = html.Div([
    dcc.Dropdown(
        id='product-dropdown',
        options=[{'label': p, 'value': p} for p in df['Product ID'].unique()],
        value=[],  # Default to show all products
        multi=True
    ),
    dcc.Graph(id='bar-chart'),
    dcc.RangeSlider(
        id='range-slider',
        min=0,
        max=len(products['Product ID'].unique()) - 10,
        step=1,
        value=[0, 10],  # Start by showing the first 10 Product IDs
        marks={i: f'{i+1}-{i+10}' for i in range(0, len(products['Product ID'].unique()), 10)}
    ),
    dcc.Graph(id='scatter-plot')
])

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('bar-chart', 'id'), Input('range-slider', 'value')]
)
def update_chart(_, range_values):
    # Select the range of Product IDs based on the range slider
    start, end = range_values[0], range_values[1]

    # Subset the DataFrame to only include the selected Product IDs
    products_filtered = products.iloc[start:end]
    products_filtered = products_filtered.sort_values(by='Profit_percent', ascending=False)

    # Create the bar chart using Plotly Express
    fig = px.bar(products_filtered, x='Product ID', y='Total_Sales',
                 color='Profit_percent',
                 color_continuous_scale=["red", "green", "blue"],
                 title='Total Sales by Product ID')

    # Update the layout to add a scroll effect for Product IDs
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=False),  # Add range slider to x-axis
            title='Product ID'
        ),
        yaxis=dict(title='Sales')
    )

    return fig

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('product-dropdown', 'value')]
)
def update_graph(selected_products):
    # If products are selected, filter the rows where any selected product is in Market_Basket
    if selected_products:
        market_basket_filtered = market_basket[market_basket['Market_Basket'].apply(
            lambda basket: any(prod in basket for prod in selected_products)
        )]
        # df[df['Market_Basket'].apply(lambda basket: any(prod in basket for prod in selected_products))]
    else:
        # If no products are selected, return the entire DataFrame
        market_basket_filtered = market_basket
    # market_basket = market_basket[market_basket['Market_Basket'].str.contains(selected_products)]
    # market_basket = market_basket[market_basket.apply(lambda row: row[selected_products] in row['Market_Basket'], axis=1)]
    print(market_basket_filtered)
    
    fig = px.scatter(
        market_basket_filtered,
        x='Profit_percent',
        y='Total_Sales',
        color='Profit_percent',
        color_continuous_scale=["red", "green", "blue"],
        size=abs(market_basket_filtered['Profit_percent']),
        text='Market_Basket',
        title='Total Profit vs. Profit Percentage',
        # labels={'Profit': 'Total Profit', 'Sales': 'Total Sales'},
        size_max=60
    )
    
    fig.update_layout(
        showlegend=True,
        xaxis_title='Profit Percentage',
        yaxis_title='Total Sales'
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)