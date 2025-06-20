from pathlib import Path
from importlib.metadata import version
import toml


from hibachi_xyz.api import *
from hibachi_xyz.types import *
from hibachi_xyz.helpers import *
from hibachi_xyz.api_ws_market import HibachiWSMarketClient
from hibachi_xyz.api_ws_trade import HibachiWSTradeClient
from hibachi_xyz.api_ws_account import HibachiWSAccountClient

def get_version() -> str:
    """Return the version of the hibachi library package."""
    pyproject_path = Path(__file__).parents[1] / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path) as f:
            pyproject = toml.loads(f.read())

        return pyproject["project"]["version"]

    return version("hibachi_xyz")

__version__: str = get_version()
__all__ = [
    "HibachiApiClient",
    "HibachiApiError",
    "Interval",
    "Nonce",
    "OrderId",
    "Side",
    "TWAPConfig",
    "TWAPQuantityMode",
    "CreateOrder",
    "UpdateOrder",
    "CancelOrder",
    "__version__",
]
