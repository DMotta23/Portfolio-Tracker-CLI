#Author: Diogo Terra Simões da Motta - 2nd Year BIE
#Course: Programming for Economists II
import yfinance as yf

# ---------------------------
# BASIC TICKER INFO
# ---------------------------
def show_basic_ticker_info(ticker):
    """
    Prints very basic info about the ticker: exchange, currency, current price.
    If it fails, it just prints a warning and continues (doesn't block the user).
    """
    try:
        tk = yf.Ticker(ticker)

        info = tk.info  # may be slow sometimes, but simplest
        exchange = info.get("exchange", "N/A")
        currency = info.get("currency", "N/A")

        hist = tk.history(period="1d")
        if hist.empty:
            print("\nWarning: No price data found.")
            print("Ticker may be invalid, delisted, or require a suffix (e.g., .SA).")
            return False
        else:
            price = float(hist["Close"].iloc[-1])

        print("\n--- Ticker info ---")
        print("Exchange:", exchange)
        print("Currency:", currency)
        print(f"Current price: {price:.2f}")
        print("-------------------\n")
        return True

    except Exception:
        print("Could not fetch ticker info.")
        return False


# ---------------------------
# MENU
# ---------------------------
def print_menu():
    print("\n==== PORTFOLIO MANAGER ====")
    print("1) Manage holdings")
    print("2) Portfolio summary (fetch prices)")
    print("3) Rebalance suggestions")
    print("0) Exit")


# ---------------------------
# HOLDINGS
# portfolio = {"AAPL": {"shares": 5.0, "avg_cost": 150.0}, ...}
# ---------------------------
def manage_holdings(portfolio):
    while True:
        print("\n-- Manage holdings --")
        print("1) Add/Update holding")
        print("2) Remove holding")
        print("3) View holdings")
        print("0) Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            ticker = input("Ticker (e.g., AAPL): ").strip().upper()
            if ticker == "":
                print("Ticker cannot be empty.")
                continue

            # show basic info after ticker is entered; if False, it skips saving and restarts while loop
            if show_basic_ticker_info(ticker) == False:
                continue

            try:
                shares = float(input("Shares: ").strip())
                avg_cost = float(input("Average cost per share: ").strip())
            except ValueError:
                print("Invalid number.")
                continue

            if shares <= 0 or avg_cost <= 0:
                print("Shares and avg_cost must be > 0.")
                continue

            portfolio[ticker] = {"shares": shares, "avg_cost": avg_cost}
            print("Saved:", ticker)

        elif choice == "2":
            ticker = input("Ticker to remove: ").strip().upper()
            if ticker in portfolio:
                del portfolio[ticker]
                print("Removed:", ticker)
            else:
                print("Not found.")

        elif choice == "3":
            if len(portfolio) == 0:
                print("Portfolio is empty.")
            else:
                for t in portfolio:
                    info = portfolio[t]
                    print(f"{t}: {info['shares']} shares @ avg cost {info['avg_cost']}")

        elif choice == "0":
            break
        else:
            print("Invalid option.")


# ---------------------------
# PRICES
# simplest possible: fetch each ticker one by one
# ---------------------------
def fetch_prices(tickers):
    prices = {}
    for t in tickers:
        try:
            hist = yf.Ticker(t).history(period="5d")
            if hist.empty:
                prices[t] = None
            else:
                prices[t] = float(hist["Close"].iloc[-1])
        except:
            prices[t] = None
    return prices


def manual_fix_prices(prices):
    fixed = {}
    for t in prices:
        p = prices[t]
        if p is not None:
            fixed[t] = p
        else:
            while True:
                try:
                    val = float(input(f"Couldn't fetch {t}. Enter price manually: ").strip())
                    if val <= 0:
                        print("Price must be > 0.")
                        continue
                    fixed[t] = val
                    break
                except:
                    print("Invalid number.")
    return fixed


# ---------------------------
# SUMMARY
# ---------------------------
def portfolio_summary(portfolio):
    if len(portfolio) == 0:
        print("\nPortfolio is empty. Add holdings first.")
        return

    tickers = []
    for t in portfolio:
        tickers.append(t)

    prices = fetch_prices(tickers)
    prices = manual_fix_prices(prices)

    total_value = 0.0
    rows = []

    for t in tickers:
        shares = portfolio[t]["shares"]
        avg_cost = portfolio[t]["avg_cost"]
        price = prices[t]
        value = shares * price
        unreal = (price - avg_cost) * shares
        total_value = total_value + value
        rows.append([t, shares, avg_cost, price, value, unreal])

    print("\n===== PORTFOLIO SUMMARY =====")
    print(f"Total value: {total_value:.2f}\n")

    # line below prints summary as float and controls width
    print(f"{'Ticker':<8} {'Shares':>10} {'AvgCost':>10} {'Price':>10} {'Value':>12}"
          f" {'Unreal P/L':>12} {'Weight':>8}")
    print("-" * 86)

    best_t = None
    best_pl = None
    worst_t = None
    worst_pl = None

    for r in rows:
        t, shares, avg_cost, price, value, unreal = r # assigning a name to each value
        if total_value > 0:
            weight = (value / total_value) * 100
        else:
            weight = 0

        print(f"{t:<8} {shares:>10.2f} {avg_cost:>10.2f} {price:>10.2f} {value:>12.2f}"
              f" {unreal:>12.2f} {weight:>7.2f}%")

        # iterating through each stock and seeing which one has the best and worst P/L
        if best_pl is None or unreal > best_pl:
            best_pl = unreal
            best_t = t
        if worst_pl is None or unreal < worst_pl:
            worst_pl = unreal
            worst_t = t

    print("\nBiggest winner (unrealized):", best_t, f"{best_pl:.2f}")
    print("Biggest loser  (unrealized):", worst_t, f"{worst_pl:.2f}")


# ---------------------------
# REBALANCE
# ---------------------------
def rebalance_suggestions(portfolio):
    if len(portfolio) == 0:
        print("Portfolio is empty.")
        return

    tickers = []
    for t in portfolio:
        tickers.append(t)

    prices = fetch_prices(tickers)
    prices = manual_fix_prices(prices)

    total_value = 0.0
    values = {}
    for t in tickers:
        v = portfolio[t]["shares"] * prices[t]
        values[t] = v
        total_value += v

    print("\nEnter target weights in % for each ticker.")
    print("Example: if you want 50%, type 50")

    targets = {}
    total_w = 0.0

    for t in tickers:
        while True:
            try:
                w = float(input(f"Target weight for {t} (in %): ").strip())
                if w < 0:
                    print("Weight must be >= 0.")
                    continue
                targets[t] = w
                total_w += w
                break
            except:
                print("Invalid number.")

    if total_w == 0: # error handling, because total weight (denominator) cannot be zero
        print("All weights are 0. Nothing to do.")
        return

    # normalize to sum to 100
    for t in targets:
        targets[t] = (targets[t] / total_w) * 100

    print("\n===== REBALANCE SUGGESTIONS =====")
    print(f"Total portfolio value: {total_value:.2f}")
    print("Targets normalized to sum to 100%.\n")

    for t in tickers:
        current_val = values[t]
        target_val = (targets[t] / 100) * total_value
        gap = target_val - current_val

        price = prices[t]  # NEW: needed to convert € gap to shares

        if gap > 0:
            if price > 0:
                shares_to_buy = gap / price
            else:
                shares_to_buy = 0
            print(f"{t}: BUY about {gap:.2f} worth (about {shares_to_buy:.2f} shares)")
        elif gap < 0:
            sell_amount = abs(gap)
            if price > 0:
                shares_to_sell = sell_amount / price
            else:
                shares_to_sell = 0
            print(f"{t}: SELL about {sell_amount:.2f} worth (about {shares_to_sell:.2f} shares)")
        else:
            print(f"{t}: already on target")


# ---------------------------
# MAIN
# ---------------------------
def main():
    portfolio = {}

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            manage_holdings(portfolio)
        elif choice == "2":
            portfolio_summary(portfolio)
        elif choice == "3":
            rebalance_suggestions(portfolio)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__": #chatgpt recommended this instead of just main()
    main()