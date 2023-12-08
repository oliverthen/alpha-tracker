import numpy as np
# Temp file that calculates beta

# Comparing Google, Amazon, and Meta return with NASDAQ Compiste for 2018 to 2022 as a test
google_stock_returns = np.array([-0.01, 0.29, 0.31, 0.65, -0.39])
amazon_stock_returns = np.array([0.28, 0.23, 0.76, 0.02, -0.50])
meta_stock_returns = np.array([-0.36, 0.90, 0.00, 0.64, -0.27])
market_returns = np.array([-0.05, 0.36, 0.39, 0.25, -0.34])

# Calculate covariance and variance
google_covariance = np.cov(google_stock_returns, market_returns)[0, 1]
amazon_covariance = np.cov(amazon_stock_returns, market_returns)[0, 1]
meta_covariance = np.cov(meta_stock_returns, market_returns)[0, 1]
variance_market = np.var(market_returns)

# Calculate beta for the 3 stocks
google_beta = google_covariance / variance_market
amazon_beta = amazon_covariance / variance_market
meta_beta = meta_covariance / variance_market

print(f"The beta for google's stock is: {google_beta}")
print(f"The beta for amazon's stock is: {amazon_beta}")
print(f"The beta for meta's stock is: {meta_beta}")
