import csv
import requests
from moralis import evm_api

api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImZjNzAyYjUyLTAzMjUtNGU5Zi05MDkwLTYyZTdiYjVkMWViOSIsIm9yZ0lkIjoiNDEzMDI1IiwidXNlcklkIjoiNDI0NDUwIiwidHlwZUlkIjoiYTdhZmQ0OWQtOGUwYi00ZDFkLTk2Y2QtMGY1ZDkzNDExODBlIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3Mjk2OTM3ODIsImV4cCI6NDg4NTQ1Mzc4Mn0.FHPAp9OlGY89_LdJcjiLH9EWA0RJIHW0OAuNdALb5gw"

# List of wallet addresses to check
wallet_addresses = [

    "0xa733dcbe5b3ae4570481158aff902ef27bf33c4c",
    '0xB75690F6916933261796A06f93Dd6a3E8706b020'
]

blockchains = ["eth", "bsc", "polygon", "avalanche", "fantom", "arbitrum", "base", "optimism", "linea"]


def get_wallet_data(wallet_address):
    portfolio_data = []
    chain_values = {}
    total_portfolio_value = 0

    for chain in blockchains:
        params = {
            "chain": chain,
            "address": wallet_address
        }

        try:
            result = evm_api.wallets.get_wallet_token_balances_price(api_key=api_key, params=params)
            tokens = result['result']
            print("tokens: ", tokens)

            if tokens:
                chain_value = 0
                for token in tokens:
                    usd_value = token.get('usd_value', 0)
                    balance_formatted = token.get('balance_formatted', 0)

                    if float(balance_formatted) == 0 and usd_value == 0:
                        continue 

                    symbol = token.get('symbol', 'Unknown')
                    usd_price = token.get('usd_price', 0)
                    balance_formatted = token.get('balance_formatted', 0)
                    usd_value = usd_value if usd_value is not None else 0
                    portfolio_percentage = token.get('portfolio_percentage', 0)
                    chain_value += usd_value
                    total_portfolio_value += usd_value

                    token_data = {
                        "chain": chain.upper(),
                        "token": symbol,
                        "portfolio_percentage": portfolio_percentage,
                        "price": f"${usd_price:.4f}" if usd_price else "$0.00",
                        "amount": f"{float(balance_formatted):,.6f}" if balance_formatted else "0.0000",
                        "value": f"${usd_value:.4f}" if usd_value else "$0.00"
                    }
                    portfolio_data.append(token_data)

                chain_values[chain] = chain_value

        except Exception as e:
            print(f"Error retrieving data for {wallet_address} on {chain}: {e}")
            chain_values[chain] = 0

    return portfolio_data, chain_values, total_portfolio_value

def write_to_csv(wallet_address, portfolio_data, chain_values, total_portfolio_value, writer):
    writer.writerow(["Wallet Address", wallet_address])
    
    capital_summary = []
    for chain, value in chain_values.items():
        percentage = (value / total_portfolio_value) * 100 if total_portfolio_value > 0 else 0
        capital_summary.append(f"{chain.upper()} ${value:,.6f} ({percentage:.4f}%)")
    writer.writerow(["Chains with Capital", ", ".join(capital_summary)])
    
    writer.writerow(["Total Funds", f"${total_portfolio_value:,.4f}"])
    writer.writerow([])

    writer.writerow(["Chain", "Token", "Portfolio %", "Price", "Amount", "Value"])
    for data in portfolio_data:
        writer.writerow([data['chain'], data['token'], f"{data['portfolio_percentage']:.4f}%", data['price'], data['amount'], data['value']])

    writer.writerow([])

def main():
    with open("wallet_portfolio_report.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        
        for wallet_address in wallet_addresses:
            portfolio_data, chain_values, total_portfolio_value = get_wallet_data(wallet_address)
            write_to_csv(wallet_address, portfolio_data, chain_values, total_portfolio_value, writer)

if __name__ == "__main__":
    main()
