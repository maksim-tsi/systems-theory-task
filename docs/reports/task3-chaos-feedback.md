Коллега, я внимательно проанализировал ваш код и полученные артефакты.Диагноз: Результаты хаос-метрик выглядят подозрительно.$H \approx 0.99$ для дневных данных — это почти прямая линия (детерминированный тренд), что крайне маловероятно для продаж.$D_2 = 0.0$ — это "точка" или константа. Это означает, что алгоритм не смог найти размерность аттрактора.Причина сбоя:Ваш код _corr_dim_gp использует эвклидовы расстояния (np.linalg.norm) на "сырых" данных.Проблема 1 (Data Sparsity): Даже после фильтрации "Daytime", в данных много нулей (стокауты). Расстояние между двумя точками (0,0) и (0,0) равно нулю. log(0) дает ошибку или отбрасывается, и алгоритм коллапсирует.Проблема 2 (Scaling): Hurst $R/S$ анализ чувствителен к трендам. Если ряд имеет сильную сезонность (день/ночь), $R/S$ может завышать показатель (что мы и видим с $H=0.99$).Решение: Переход на версию "Graphic as a Code"Код, который я предложил вам в предыдущем сообщении (src/chaos_metrics.py и src/visualization.py), решает эти проблемы:Robust Hurst: Мой алгоритм calculate_hurst_rs использует логарифмическую сетку окон и линейную регрессию, отбрасывая окна с нулевым отклонением ($S=0$). Это спасет от нулей.Robust D2: Мой алгоритм correlation_dimension использует KDTree (или оптимизированный pdist) и логарифмические радиусы, фильтруя нулевые расстояния до логарифмирования.Визуализация: Самое главное — вы увидите график. Если точки лежат на прямой — метрика верна. Если "облако" — метрика мусор, и мы это увидим глазами.Я настоятельно рекомендую заменить текущие chaos_metrics.py и создать visualization.py по моему плану.


## Почему "Graphic as a Code" (Python) лучше для PhD:

1. **Воспроизводимость:** В Fractan вы "выделили мышкой область". В Python мы алгоритмически фиксируем диапазон.
2. **Интерактивность:** HTML-отчет с Plotly позволит вам зумить графики, чтобы проверить линейность наклона (scaling law) так же детально, как в спец. софте.

---

### План реализации Task 3 (HTML Report)

Мы создадим три модуля:

1. `src/chaos_metrics.py`: Математическое ядро (аналог движка Fractan).
2. `src/visualization.py`: Генерация интерактивных фигур Plotly (аналог графического интерфейса).
3. `src/report_generator.py`: Скрипт, который соберет текст и графики в единый HTML-файл.

Приступаем к реализации ядра и визуализации.

#### Шаг 1. Математическое ядро (`src/chaos_metrics.py`)

Этот модуль реализует R/S анализ и Correlation Dimension.

```python
"""Chaos Theory metrics: Hurst Exponent and Correlation Dimension.

Implements algorithms typically found in fractal analysis software (e.g. Fractan).
"""
from typing import Tuple, List, Dict, Any
import numpy as np
from sklearn.linear_model import LinearRegression

def time_delay_embedding(series: np.ndarray, delay: int, dim: int) -> np.ndarray:
    """Create a time-delay embedding of the time series (Phase Space Reconstruction)."""
    n = len(series)
    if n < (dim - 1) * delay + 1:
        raise ValueError("Series too short for this embedding")
    
    # Efficient numpy stride trick or simple loop
    vectors = []
    for i in range(n - (dim - 1) * delay):
        vectors.append(series[i : i + dim * delay : delay])
    return np.array(vectors)

def calculate_hurst_rs(series: np.ndarray, min_chunk: int = 8) -> Dict[str, Any]:
    """Calculate Hurst Exponent using R/S Analysis.
    
    Returns:
        Dict containing 'H' (slope), 'scales' (log n), 'rs_values' (log R/S).
    """
    series = np.array(series, dtype=float)
    N = len(series)
    
    # Log-spaced scales (window sizes)
    max_chunk = N // 2
    scales = np.unique(np.logspace(np.log10(min_chunk), np.log10(max_chunk), num=20).astype(int))
    scales = scales[scales > 4] # Filter tiny windows
    
    rs_values = []
    
    for n in scales:
        # Split into chunks of size n
        num_chunks = N // n
        chunks_rs = []
        
        for i in range(num_chunks):
            chunk = series[i*n : (i+1)*n]
            mean = np.mean(chunk)
            # Cumulative deviation
            y = np.cumsum(chunk - mean)
            # Range
            R = np.max(y) - np.min(y)
            # Standard deviation
            S = np.std(chunk, ddof=1)
            
            if S == 0: continue
            chunks_rs.append(R / S)
            
        if chunks_rs:
            rs_values.append(np.mean(chunks_rs))
        else:
            rs_values.append(np.nan)
            
    # Remove NaNs
    valid = ~np.isnan(rs_values)
    scales = scales[valid]
    rs_values = np.array(rs_values)[valid]
    
    if len(scales) < 3:
        return {"H": 0.5, "valid": False} # Not enough data
        
    # Fit line in log-log space
    log_n = np.log10(scales)
    log_rs = np.log10(rs_values)
    
    model = LinearRegression()
    model.fit(log_n.reshape(-1, 1), log_rs)
    H = model.coef_[0]
    
    return {
        "H": H,
        "scales_log": log_n,
        "rs_log": log_rs,
        "r2": model.score(log_n.reshape(-1, 1), log_rs),
        "valid": True
    }

def correlation_integral(embedded_data: np.ndarray, radius: float) -> float:
    """Calculate Correlation Sum C(r) - fraction of pairs closer than r."""
    # Using KDTree for optimization is better, but pure numpy for strict envs
    # Calculating pairwise distances (Euclidean)
    # WARNING: O(N^2), use subsample for large data
    from scipy.spatial.distance import pdist
    
    dists = pdist(embedded_data, metric='euclidean')
    count = np.sum(dists < radius)
    return count / len(dists)

def correlation_dimension(series: np.ndarray, dim: int = 3, delay: int = 1) -> Dict[str, Any]:
    """Estimate Correlation Dimension (D2) via Grassberger-Procaccia."""
    # Limit data size for performance
    if len(series) > 1000:
        series_sub = series[:1000] # Use first 1000 points
    else:
        series_sub = series
        
    embedded = time_delay_embedding(series_sub, delay, dim)
    
    # Calculate pairwise distances once to define radius range
    from scipy.spatial.distance import pdist
    dists = pdist(embedded, metric='euclidean')
    dists = dists[dists > 0]
    
    if len(dists) == 0:
        return {"D2": 0.0, "valid": False}
        
    min_r, max_r = np.min(dists), np.max(dists)
    
    # Log-spaced radii
    radii = np.logspace(np.log10(min_r * 1.5), np.log10(max_r * 0.5), num=15)
    c_r = []
    
    for r in radii:
        count = np.sum(dists < r)
        c_val = count / len(dists)
        c_r.append(c_val)
        
    # Filter valid log values
    radii = np.array(radii)
    c_r = np.array(c_r)
    valid = (c_r > 0) & (c_r < 1)
    
    if np.sum(valid) < 3:
        return {"D2": 0.0, "valid": False}
        
    log_r = np.log10(radii[valid])
    log_c = np.log10(c_r[valid])
    
    # Fit line
    model = LinearRegression()
    model.fit(log_r.reshape(-1, 1), log_c)
    D2 = model.coef_[0]
    
    return {
        "D2": D2,
        "radii_log": log_r,
        "cr_log": log_c,
        "r2": model.score(log_r.reshape(-1, 1), log_c),
        "valid": True
    }

```

#### Шаг 2. Визуализация (`src/visualization.py`)

Этот модуль создаст интерактивные графики для вставки в HTML.

```python
"""Visualization module for Systems Theory Analysis.

Generates Plotly figures for Time Series, Phase Portraits, and Chaos Metrics.
Returns HTML strings or Figure objects.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def plot_time_series(df: pd.DataFrame) -> go.Figure:
    """Interactive plot of Sales vs Stockouts."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=df['dt_hour'], y=df['sales'], name="Sales", line=dict(color='blue', width=1)),
        secondary_y=False
    )
    
    # Highlight stockouts
    stockouts = df[df['is_stockout'] == 1]
    fig.add_trace(
        go.Scatter(x=stockouts['dt_hour'], y=stockouts['sales'], mode='markers', 
                   name="Stockout Event", marker=dict(color='red', size=4)),
        secondary_y=False
    )
    
    fig.update_layout(title="Inventory Dynamics: Sales & Stockouts", template="plotly_white")
    return fig

def plot_phase_portrait(series: np.ndarray, delay: int = 1) -> go.Figure:
    """2D Phase Portrait (x(t) vs x(t+tau))."""
    x = series[:-delay]
    y = series[delay:]
    
    fig = go.Figure(data=go.Scatter(
        x=x, y=y, mode='lines', 
        line=dict(width=0.5, color='purple'), opacity=0.7
    ))
    fig.update_layout(
        title=f"Phase Space Reconstruction (delay={delay})",
        xaxis_title="x(t)",
        yaxis_title=f"x(t+{delay})",
        template="plotly_white",
        width=600, height=600
    )
    return fig

def plot_hurst_fit(metrics: dict) -> go.Figure:
    """Log-Log plot for R/S Analysis."""
    log_n = metrics['scales_log']
    log_rs = metrics['rs_log']
    H = metrics['H']
    
    fig = go.Figure()
    # Data points
    fig.add_trace(go.Scatter(x=log_n, y=log_rs, mode='markers', name='R/S Data'))
    
    # Regression line
    line_y = log_rs[0] + H * (log_n - log_n[0]) # approx line
    fig.add_trace(go.Scatter(x=log_n, y=line_y, mode='lines', name=f'Fit (H={H:.3f})'))
    
    fig.update_layout(
        title=f"Hurst Exponent Estimation (H={H:.3f})",
        xaxis_title="log(n) [Time Scale]",
        yaxis_title="log(R/S) [Rescaled Range]",
        template="plotly_white"
    )
    return fig

def plot_correlation_dim(metrics: dict) -> go.Figure:
    """Log-Log plot for Correlation Dimension."""
    log_r = metrics['radii_log']
    log_c = metrics['cr_log']
    D2 = metrics['D2']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=log_r, y=log_c, mode='markers', name='C(r) Data'))
    
    # Regression line
    line_y = log_c[0] + D2 * (log_r - log_r[0])
    fig.add_trace(go.Scatter(x=log_r, y=line_y, mode='lines', name=f'Fit (D2={D2:.3f})'))
    
    fig.update_layout(
        title=f"Correlation Dimension (D2={D2:.3f})",
        xaxis_title="log(r) [Radius]",
        yaxis_title="log(C(r)) [Correlation Sum]",
        template="plotly_white"
    )
    return fig

```

### Следующие действия

1. Создай файлы `src/chaos_metrics.py` и `src/visualization.py` с кодом выше.
2. Затем подготовь финальный скрипт `src/generate_task3_report.py`, который:
* Загрузит `golden_sample.parquet`.
* Посчитает метрики.
* Сгенерирует HTML с графиками.
* Сохранит его как `docs/reports/task3_chaos_report.html`.