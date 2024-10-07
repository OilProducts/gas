import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, _dash_renderer

_dash_renderer._set_react_version("18.2.0")

# Initialize the app
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

navbar = dmc.AppShellNavbar(
    [
        dmc.NavLink(
            label="Home",
            href="/",
        ),
        dmc.NavLink(
            label="Roles",
            href="/roles",
        ),
        dmc.NavLink(
            label="Events",
            href="/events",
        ),
        dmc.NavLink(
            label="Conversation",
            href="/conversation",
        )
    ],
)

app.layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dmc.AppShellHeader("placeholder"),
            navbar,
            dmc.AppShellMain(dash.page_container,
                             id="page-content"
            ),
        ],
        header={'height': '25'},
        navbar={'width': '200'}
    )
)

if __name__ == '__main__':
    app.run(debug=True)
