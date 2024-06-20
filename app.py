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

        df = df.sort_index(ascending=False)
        df = df.head(145)

        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date'}, inplace=True)

        close_prices = df['Close'].tolist()
        open_prices = df['Open'].tolist()
        hundredMA = df['100d MA'].tolist()
        fiftyMA = df['50d MA'].tolist()
        dates = df['Date'].dt.strftime('%m-%d-%Y').tolist()

        dates.reverse()
        close_prices.reverse()
        open_prices.reverse()
        hundredMA.reverse()
        fiftyMA.reverse()

        data = {"date" : dates,
            "close": close_prices,
            "open": open_prices,
            "hundredMA": hundredMA,
            "fiftyMA": fiftyMA}

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
    close_prices = [float(x) for x in request.args.getlist('close')]
    open_prices = [float(x) for x in request.args.getlist('open')]
    hundredMA = [float(x) for x in request.args.getlist('hundredMA')]
    fiftyMA = [float(x) for x in request.args.getlist('fiftyMA')]

    fig, ax = plt.subplots()
    dates = request.args.getlist('date')

    ax.plot(dates, open_prices, label='Open')
    ax.plot(dates, close_prices, label='Close')
    ax.plot(dates, hundredMA, label='100d MA')
    ax.plot(dates, fiftyMA, label='50d MA')
    
    ax.legend()
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_formatter))

    plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=10))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=20))
    plt.xticks(rotation=90)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug = True)