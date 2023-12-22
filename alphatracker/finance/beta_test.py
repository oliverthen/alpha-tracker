# File meant to just test beta function
# import numpy as np
# import yfinance as yf

# goog = yf.Ticker("GOOG")
# print(goog)
# data = goog.history(start="2018-01-01", end="2023-1-2", interval='3mo')
# open_list = data["Open"].tolist()


# start_year_price = []
# i = 0
# for open_price in open_list:
#     # Since interval for history is 3 months, it means there are 4 sets of dates per year. Since we only want the open price for first date of year, we set i to 0, save that price, and then skip over the other prices since i is not 0. Once i becomes 3, we then turn it back to 0 to save that price
#     if i == 0:
#         start_year_price.append(open_price)
#         i += 1
#     else:
#         if i == 3:
#             i = 0
#         else:
#             i += 1

# asset_returns = []
# prev = None
# for price in start_year_price:
#     if prev is None:
#         prev = price
#     else:
#         asset_return = (price - prev) / prev
#         asset_returns.append(round(asset_return, 2))
#         prev = price
# print(asset_returns)

# asset_stock_returns = np.array(asset_returns)
# market_returns = np.array([-0.05, 0.36, 0.39, 0.25, -0.34])

# # Calculate covariance and variance
# asset_covariance = np.cov(asset_stock_returns, market_returns)[0, 1]
# variance_market = np.var(market_returns)

# # Calculate beta for the asset
# asset_beta = asset_covariance / variance_market
# print(asset_beta)  

# Temp file that calculates beta

# # Comparing Google, Amazon, and Meta return with NASDAQ Compiste for 2018 to 2022 as a test
# google_stock_returns = np.array([-0.01, 0.29, 0.31, 0.65, -0.39])
# amazon_stock_returns = np.array([0.28, 0.23, 0.76, 0.02, -0.50])
# meta_stock_returns = np.array([-0.36, 0.90, 0.00, 0.64, -0.27])
# market_returns = np.array([-0.05, 0.36, 0.39, 0.25, -0.34])

# # Calculate covariance and variance
# google_covariance = np.cov(google_stock_returns, market_returns)[0, 1]
# amazon_covariance = np.cov(amazon_stock_returns, market_returns)[0, 1]
# meta_covariance = np.cov(meta_stock_returns, market_returns)[0, 1]
# variance_market = np.var(market_returns)

# # Calculate beta for the 3 stocks
# google_beta = google_covariance / variance_market
# amazon_beta = amazon_covariance / variance_market
# meta_beta = meta_covariance / variance_market

# print(f"The beta for google's stock is: {google_beta}")
# print(f"The beta for amazon's stock is: {amazon_beta}")
# print(f"The beta for meta's stock is: {meta_beta}")
