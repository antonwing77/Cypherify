import plotly.graph_objects as go
from collections import Counter

def create_frequency_chart(freq_data: Counter):
    """Create a bar chart for letter frequency analysis."""
    if not freq_data:
        return go.Figure()
    
    letters = sorted(freq_data.keys())
    counts = [freq_data[letter] for letter in letters]
    
    fig = go.Figure(data=[
        go.Bar(x=letters, y=counts, marker_color='steelblue')
    ])
    
    fig.update_layout(
        title='Letter Frequency Distribution',
        xaxis_title='Letter',
        yaxis_title='Frequency',
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

# By Anton Wingeier

def create_rsa_diagram(p, q, n, e, d, phi):
    """Create a visual diagram of RSA key generation."""
    fig = go.Figure()
    
    # Create annotations showing the RSA process
    annotations = [
        dict(x=0.5, y=0.9, text=f'<b>Prime Numbers</b><br>p = {p}, q = {q}',
             showarrow=False, font=dict(size=12)),
        dict(x=0.5, y=0.7, text=f'<b>Calculate n</b><br>n = p × q = {n}',
             showarrow=False, font=dict(size=12)),
        dict(x=0.5, y=0.5, text=f'<b>Calculate φ(n)</b><br>φ(n) = (p-1)(q-1) = {phi}',
             showarrow=False, font=dict(size=12)),
        dict(x=0.2, y=0.25, text=f'<b>Public Key</b><br>(e={e}, n={n})',
             showarrow=False, font=dict(size=11), bgcolor='lightgreen'),
        dict(x=0.8, y=0.25, text=f'<b>Private Key</b><br>(d={d}, n={n})',
             showarrow=False, font=dict(size=11), bgcolor='lightcoral'),
    ]
    
    fig.update_layout(
        annotations=annotations,
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='white'
    )
    
    return fig

def create_block_diagram(blocks, key_size):
    """Create a diagram showing AES block structure."""
    fig = go.Figure()
    
    # Create block visualization
    for i in range(min(blocks, 8)):  # Show max 8 blocks
        fig.add_shape(
            type="rect",
            x0=i*1.2, y0=0, x1=i*1.2+1, y1=1,
            line=dict(color="steelblue", width=2),
            fillcolor="lightblue"
        )
        fig.add_annotation(
            x=i*1.2+0.5, y=0.5,
            text=f"Block {i+1}<br>16 bytes",
            showarrow=False,
            font=dict(size=10)
        )
    
    if blocks > 8:
        fig.add_annotation(
            x=8*1.2+0.5, y=0.5,
            text=f"...+{blocks-8} more",
            showarrow=False,
            font=dict(size=10)
        )
    
    fig.update_layout(
        title=f'AES Block Structure ({key_size}-bit key, {blocks} blocks)',
        xaxis=dict(visible=False, range=[-0.5, max(8*1.2+1, blocks*1.2)]),
        yaxis=dict(visible=False, range=[-0.2, 1.2]),
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white'
    )
    
    return fig
