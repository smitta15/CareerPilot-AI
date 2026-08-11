from contextlib import contextmanager

from pathlib import Path

try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:  # pragma: no cover - depends on optional package install
    SqliteSaver = None

from langgraph.checkpoint.memory import InMemorySaver


@contextmanager
def checkpoint():
    if SqliteSaver is None:
        yield InMemorySaver()
        return

    database_path = Path(__file__).resolve().parents[2] / "careerpilot.db"
    with SqliteSaver.from_conn_string(str(database_path)) as saver:

        saver.setup()

        yield saver
