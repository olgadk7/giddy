import plotly.graph_objects as go
import colorcet as cc

def plot_total_keywords_counts(posts_df, price_df):
    # Create a line plot for the row counts
    trace1 = go.Scatter(
        x=posts_df.index, y=posts_df['total_mentions'], # hourly is the appropriate granularity
        mode='lines',
        name='Giddy Keyword Count'
    )

    # Create a OHLC plot for the price
    trace2 = go.Candlestick(
        x=price_df['Date'],
        open=price_df['Open'],
        high=price_df['High'],
        low=price_df['Low'],
        close=price_df['Close'],
        name='Price')

    # # Create a line plot for the closing prices
    # trace2 = go.Scatter(
    #     x=gme_df['Date'], # there's only dayly price available
    #     y=gme_df['Close'],
    #     mode='lines',
    #     name='GME Closing Prices'
    # )

    # Create a line plot for the closing prices
    trace3 = go.Scatter(
        x=price_df['Date'], # there's only dayly price available
        y=price_df['sma20'],
        mode='lines',
        name='MA20'
    )

    trace4 = go.Scatter(
        x=price_df['Date'], # there's only dayly price available
        y=price_df['sma5'],
        mode='lines',
        name='MA5'
    )

    trace5 = go.Scatter(
        x=price_df['Date'], # there's only dayly price available
        y=price_df['ema_5'],
        mode='lines',
        name='EMA_5'
    )


    # Combine the two plots
    layout = go.Layout(title={'y':0.93, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                       legend=dict(orientation="h", y=1.15, x=0.5, xanchor='center'),
                       yaxis=dict(title='Count & Price'))

    fig = go.Figure(data=[trace1, trace2, trace3, trace4, trace5], layout=layout)

    # fig.write_html('giddy_mentions_total_keywords_counts.html', auto_open=True)

    # Show the plot
    fig.show()

    





def plot_total_keyword_percentage(posts_df, price_df, annotations=None):

    # Create a line plot for the row counts
    trace1 = go.Bar(
        x=posts_df.index, y=posts_df['percentage'], # hourly is the appropriate granularity
        name='Keyword percentage of total chatter',
        yaxis='y1',
        marker=dict(
            color='blue',
            line=dict(width=0),
            opacity=0.3  # Ensure bars are fully opaque
        )
    )

    # Create a OHLC plot for the price
    trace2 = go.Candlestick(
        x=price_df['Date'],
        open=price_df['Open'],
        high=price_df['High'],
        low=price_df['Low'],
        close=price_df['Close'],
        name='Price',
        yaxis='y2',
    )

    # # Create a line plot for the closing prices
    # trace2 = go.Scatter(
    #     x=gme_df['Date'],
    #     y=gme_df['Close'],
    #     mode='lines',
    #     name='GME Closing Prices',
    #     yaxis='y2',
    # )

    # Combine the two plots
    layout = go.Layout(title={'y':0.93, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                       legend=dict(orientation="h", y=1.15, x=0.5, xanchor='center'),
                       yaxis=dict(ticksuffix="%"), 
                       yaxis2=dict(side='right', overlaying='y', tickprefix="$"),
                       annotations=annotations
                      )

    fig = go.Figure(data=[trace1, trace2], layout=layout)

    # Show the plot
    fig.show()

    # fig.write_html('giddy_mentions_total_keyword_percentage.html', auto_open=True)



def plot_per_keyword_percentages(per_keyword_df, price_df):

    data = []

    # List of columns to be plotted
    cols = per_keyword_df.columns  # replace with your actual columns

    # Get color scale excluding red
    color_scale = cc.glasbey_cool

    # Calculate maximum values for each column
    column_max_values = per_keyword_df.max()

    # Create color map
    column_colors = {column: color_scale[i] for i, column in enumerate(column_max_values.sort_values().index)}

    # colors = ['blue', 'green', 'purple', 'orange']#, 'yellow']

    # Add traces to the plot
    for col in cols:
        trace = go.Scatter(
            x=per_keyword_df.index,
            y=per_keyword_df[col],
            name=col,
            yaxis='y1',
            line=dict(color=column_colors[col])  # Use color map
    #         line=dict(color=colors[i % len(colors)])  # Choose a color from the list

        )
        data.append(trace)

    # If there's a column for the right y-axis
    trace_price = go.Scatter(
        x=price_df['Date'],
        y=price_df['Close'],
        mode='lines',
        name='GME',
        showlegend=False,
        line=dict(color='red'),  # choose a color
        yaxis='y2'
    )
    data.append(trace_price)

    layout = go.Layout(
        title={
            'text': 'Giddy Mentions on r/wallstreetbets and Closing Prices<br><sub>where giddy mentions are strings expressing bewildernment</sub><br><sub>represented as a percentage of total chatter that day</sub>',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend=dict(
            orientation="h", # "h" stands for horizontal
            y=1.255,  # position legend at the top
            x=0.5,  # center the legend
            xanchor='center',  # anchor the x position at the center of the legend
        ),

        yaxis=dict(ticksuffix='%' 
        ),

        yaxis2=dict(tickprefix='$', side='right', overlaying='y'
        ),

    #     autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=100,  # Increasing right margin to add space between the y-axis and the legend
            t=180,
        )

    )

    fig = go.Figure(data=data, layout=layout)

    fig.show()

    # fig.write_html('giddy_mentions_breakdown.html', auto_open=True)
