import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_portfolio_base(
                stats, 
                correlation,
                variables={
                    'mean_ret': 'max',
                    'std_ret': 'min',
                    },
                n_assets=5,
                min_weight=0.1,
                sort_by={
                    'mean_ret': 'desc',
                    'std_ret': 'asc',
                    'corr': 'asc',
                }
                ):
    """
    get portfolio with given weights and optimization variables

    Parameters
    ----------
    stats : pd.DataFrame
        stats of the assets obtained from the DataSource class
    correlation : pd.DataFrame
        correlation matrix of the assets obtained from the DataSource class
    variables : dict
        optimization variables and their optimization function
    n_assets : int
        number of assets in the portfolio
    min_weight : float
        minimum weight of an asset in the portfolio
    sort_by : dict
        sort the portfolio by the given variables

    """
    symbols = stats.index
    
    
    # get all possible combinations of n_assets
    from itertools import combinations
    if n_assets > len(symbols):
        n_assets = len(symbols)
    comb = list(combinations(symbols, n_assets))
    
    # find optimal weights for each combination
    def objective(weights):
        test_var = 0
        c_stats = stats.loc[c]
        for v, func in variables.items():
            if func == 'max':
                test_var += -weights@c_stats[v]
            elif func == 'min':
                test_var -= +weights@c_stats[v]
        return test_var
    
    #create.all portfolios
    portfolios = []
    for c in comb:
        c = list(c)
        c_stats = stats.loc[c]
        c_corr = correlation.loc[c, c]
        
        # get the weights that perform best
        from scipy.optimize import minimize
        w = np.random.rand(n_assets)
        w /= np.sum(w)

        # weights optimization
        res = minimize(objective, w, method='SLSQP', bounds=[(0, 1)]*n_assets, 
                       constraints=[{'type': 'eq', 'fun': lambda x: np.sum(x)-1},
                                    {'type': 'ineq', 'fun': lambda x:x-min_weight}])
        w = res.x

        # save the portfolio and its stats
        c_corr = w.dot(c_corr).dot(res.x)
        c_stats = [c_stats[v].dot(w) for v in variables.keys()]
        p = {'assets': c, 'weights': w, 'corr': c_corr}
        for i, (v, func) in enumerate(variables.items()):
            p[v] = c_stats[i]
        portfolios.append(p)

    # pick the potfolio with the best stats
    portfolios = pd.DataFrame(portfolios)
    order = [True if func == 'asc' else False for func in sort_by.values()]
    portfolios = portfolios.sort_values(by=list(sort_by.keys()), ascending=order)
    portfolios = portfolios.reset_index(drop=True)

    return portfolios
