from flask import Flask, render_template, request, send_file
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from io import BytesIO

app = Flask(__name__)

def dollar_formatter(x, pos):
    return f'${x:.2f}'

@app.route('/')
def home():
    return render_template('index.html', length = 0)


@app.route('/greet', methods=['POST'])
def greet():
    name = request.form['name'].upper()
    stock = yf.Ticker(name)
    df = stock.history('1y')
    table_html = None
    data = None
    if len(df) > 0:
        df['50d MA'] = df['Close'].rolling(window=50).mean()
        df['100d MA'] = df['Close'].rolling(window=100).mean()

        open_prices = df['Open'].tolist()
        close_prices = df['Close'].tolist()
        high_prices = df['High'].tolist()
        low_prices = df['Low'].tolist()

        df = df.sort_index(ascending=False)
        df = df.head(20)

        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date'}, inplace=True)

        open_prices = df['Open'].tolist()
        close_prices = df['Close'].tolist()
        high_prices = df['High'].tolist()
        low_prices = df['Low'].tolist()
        dates = df['Date'].dt.strftime('%m-%d-%Y').tolist()

        dates.reverse()
        open_prices.reverse()
        close_prices.reverse()
        high_prices.reverse()
        low_prices.reverse()

        print(len(dates))
        print(dates)

        data = {"date" : dates,
            "open": open_prices,
            "close": close_prices,
            "high": high_prices,
            "low": low_prices}

        df['Open'] = df['Open'].round(2).apply(lambda x: f"${x:,.2f}")
        df['High'] = df['High'].round(2).apply(lambda x: f"${x:,.2f}")
        df['Low'] = df['Low'].round(2).apply(lambda x: f"${x:,.2f}")
        df['Close'] = df['Close'].round(2).apply(lambda x: f"${x:,.2f}")
        df['50d MA'] = df['50d MA'].round(2).apply(lambda x: f"${x:,.2f}")
        df['100d MA'] = df['100d MA'].round(2).apply(lambda x: f"${x:,.2f}")

        table_html = df.to_html(classes='table table-striped', index=False)

    return render_template('index.html', name=name, table_html=table_html, length = len(df), data = data)

@app.route('/plot.png')
def plot_png():
    # Extract data from query parameters
    open_prices = [float(x) for x in request.args.getlist('open')]
    close_prices = [float(x) for x in request.args.getlist('close')]
    high_prices = [float(x) for x in request.args.getlist('high')]
    low_prices = [float(x) for x in request.args.getlist('low')]

    fig, ax = plt.subplots()
    dates = request.args.getlist('date')

    ax.plot(dates, open_prices, label='Open')
    ax.plot(dates, close_prices, label='Close')
    ax.plot(dates, high_prices, label='High')
    ax.plot(dates, low_prices, label='Low')
    
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_formatter))

    plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=10))
    plt.xticks(rotation=90)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug = True)