def profit(month_sale, monthly_profit_list):
    if not monthly_profit_list:
        jan_profit = 0
        feb_profit = 0
        mar_profit = 0
        apr_profit = 0
        may_profit = 0
        jun_profit = 0
        jul_profit = 0
        aug_profit = 0
        sep_profit = 0
        oct_profit = 0
        nov_profit = 0
        dec_profit = 0
    else:
        jan_profit = monthly_profit_list[0]
        feb_profit = monthly_profit_list[1]
        mar_profit = monthly_profit_list[2]
        apr_profit = monthly_profit_list[3]
        may_profit = monthly_profit_list[4]
        jun_profit = monthly_profit_list[5]
        jul_profit = monthly_profit_list[6]
        aug_profit = monthly_profit_list[7]
        sep_profit = monthly_profit_list[8]
        oct_profit = monthly_profit_list[9]
        nov_profit = monthly_profit_list[10]
        dec_profit = monthly_profit_list[11]

    if month_sale.get_created_datetime()[3:-5] == "01":
        jan_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "02":
        feb_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "03":
        mar_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "04":
        apr_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "05":
        may_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "06":
        jun_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "07":
        jul_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "08":
        aug_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "09":
        sep_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "10":
        oct_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "11":
        nov_profit += calculate_profit(month_sale)
    elif month_sale.get_created_datetime()[3:-5] == "12":
        dec_profit += calculate_profit(month_sale)
    profit_list = [jan_profit,feb_profit,mar_profit,apr_profit,mar_profit,jun_profit,jul_profit,aug_profit,sep_profit,oct_profit,nov_profit,dec_profit]
    return profit_list


def calculate_profit(sale):
    return (float(sale.product.retail_price)-float(sale.product.get_cost_price()))*float(sale.quantity)


def calculate_sale(sale):
    return float(sale.product.retail_price)*float(sale.quantity)


def reformat_list(profit_list):
    new_profit_list = []
    for i in profit_list:
        new_profit_list.append(f'{i:.2f}')
    return new_profit_list
