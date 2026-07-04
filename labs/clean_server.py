"""Serveur MCP factice sans piège, utilisé comme cible de référence
pour valider la connexion du scanner (pas de faux positif attendu)."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clean-lab-server")


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Additionne deux nombres entiers."""
    return a + b


@mcp.tool()
def get_weather(city: str) -> str:
    """Retourne une météo factice pour une ville donnée."""
    return f"Il fait beau à {city}."


if __name__ == "__main__":
    mcp.run()
