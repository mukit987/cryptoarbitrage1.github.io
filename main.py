import func_arbitrage  # Import the other file where functions are defined
import json
import time
from datetime import datetime

# Set Variables
coins_url = "https://api.poloniex.com/markets/price"
coin_price_url = "https://api.poloniex.com/markets/ticker24h"

def create_html_file(filename='arbitrage_results.html'):
    func_arbitrage.create_html_structure(filename)

def save_to_html(result, execution_time, start_time_str, end_time_str, filename='arbitrage_results.html'):
    func_arbitrage.append_to_html(result, execution_time, start_time_str, end_time_str, filename)

def close_html_file(filename='arbitrage_results.html'):
    func_arbitrage.finalize_html_structure(filename)

def step_0():
    coin_json = func_arbitrage.get_coin_tickers(coins_url)
    coin_list = func_arbitrage.collect_tradeables(coin_json)
    return coin_list

def step_1(coin_list):
    structured_list = func_arbitrage.structure_triangular_pairs(coin_list)
    with open("structured_triangular_pairs.json", "w") as fp:
        json.dump(structured_list, fp)

def step_2():
    start_time = time.time()
    start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("structured_triangular_pairs.json") as json_file:
        structured_pairs = json.load(json_file)

    prices_json = func_arbitrage.get_coin_tickers(coin_price_url)

    for t_pair in structured_pairs:
        time.sleep(0.3)
        prices_dict = func_arbitrage.get_price_for_t_pair(t_pair, prices_json)
        surface_arb = func_arbitrage.calc_triangular_arb_surface_rate(t_pair, prices_dict)
        if len(surface_arb) > 0:
            print("Running orderbook")
            real_rate_arb = func_arbitrage.get_depth_from_orderbook(surface_arb)
            print(real_rate_arb)
            if real_rate_arb:
                end_time = time.time()
                execution_time = end_time - start_time
                end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_to_html(real_rate_arb, execution_time, start_time_str, end_time_str)
            time.sleep(20)

    end_time = time.time()
    execution_time = end_time - start_time
    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Execution time for this iteration: {execution_time:.2f} seconds")

if __name__ == "__main__":
    create_html_file()
    try:
        while True:
            step_2()
    except KeyboardInterrupt:
        close_html_file()
        print("HTML file closed and saved.")