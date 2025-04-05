def forecast_series(values, forecast_horizon):
    """
    Realiza una predicción simple usando regresión lineal sobre la serie de datos.
    Si hay menos de 2 datos, retorna el último valor repetido 'forecast_horizon' veces.
    """
    import numpy as np

    n = len(values)
    if n < 2:
        return [values[-1]] * forecast_horizon
    x = np.arange(n)
    # Ajuste lineal: y = a*x + b
    a, b = np.polyfit(x, values, 1)
    predictions = []
    for i in range(1, forecast_horizon + 1):
        pred = a * (n - 1 + i) + b
        predictions.append(pred)
    return predictions

def format_number(value):
    """
    Formatea un número con separadores de miles y dos decimales.
    """
    try:
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")  # Formato europeo
    except (ValueError, TypeError):
        return value