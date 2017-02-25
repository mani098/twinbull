def calculate_charges(stock_price=0, quantity=0):
    """
    Calculate charges for equity delivery
    :param stock_price: <Float>
    :param quantity: <Int>
    :return: <Float>
    """

    traded_value = (stock_price * quantity) / 100

    brokerage = 0  # Zero brokerage for equity delivery
    stt = traded_value * 0.1  # 0.1 % for buy & sell
    transaction_charges = traded_value * 0.00325  # NSE: 0.00325%
    service_tax = ((brokerage + transaction_charges) / 100) * 15  # 15% on (brokerage + transaction charges)
    sebi_charges = 20  # Rs.20 per crore
    stamp_duty = traded_value * 0.01  # 0.01% - max Rs. 50
    if stamp_duty >= 50:
        stamp_duty = 50

    return brokerage + stt + transaction_charges + service_tax + sebi_charges + stamp_duty
