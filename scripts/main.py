import plotly.express as px
import pandas as pd

df = pd.read_csv("data/wind_farms.csv")
df["Diameter"] = df["Diameter"].fillna(50)

fig = px.scatter_map(df, lat="Lat", lon="Lon", 
                    size="Diameter",
                    zoom=5, hover_data=["Diameter", "Hub Height", "Total Height", "Manufacturer", "Model", "Operator", "Rated Power", "Start Date"])   # country, wind farm, last update

fig.update_traces(
    cluster=dict(enabled=True, maxzoom=7)
    )


# Set map style
fig.update_layout(mapbox_style="open-street-map")

# Save to HTML
html_file = "index.html"
fig.write_html(html_file, include_plotlyjs="inline", full_html=True)

fig.show()

# Modify html head
manifest_block = """
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2c3e50">
"""

# Service worker registration for <body>
service_worker_script = """
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('service-worker.js')
            .then(reg => console.log('Service Worker registered:', reg))
            .catch(err => console.error('Service Worker registration failed:', err));
    }
</script>
"""

# Modify the HTML
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Insert manifest block into <head>
html_content = html_content.replace("<head>", "<head>\n" + manifest_block, 1)

# Custom CSS for hover box styling
custom_css = """
<style>
    .hoverlayer .hovertext {
        font-size: 36px !important;
        padding: 20px !important;
    }
</style>
"""

splash_css = """
<style>
    #splash-screen {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: #1287cd;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    #splash-screen img {
        width: 900;
        height: 900px;
    }
    #splash-screen h1 {
        color: white;
        font-size: 48px;
        margin-top: 20px;
    }
</style>
"""

splash_html = """
<div id="splash-screen">
    <img src="icon-512.png" alt="Logo">
    <h1>Wind Farms Map</h1>
</div>
<script>
    setTimeout(() => {
        document.getElementById('splash-screen').style.display = 'none';
    }, 4000);
</script>
"""

# Insert splash CSS into <head>
html_content = html_content.replace("<head>", "<head>\n" + splash_css, 1)

# Insert splash HTML into <body>
html_content = html_content.replace("<body>", "<body>\n" + splash_html, 1)

# Save the updated HTML
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

