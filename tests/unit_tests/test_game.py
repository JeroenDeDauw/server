from unittest import mock
import pytest

from games.game import Game, GameState, GameError
from src.gameconnection import GameConnection, GameConnectionState


@pytest.fixture()
def game(db):
    mock_parent = mock.Mock()
    mock_parent.db = db
    return Game(42, mock_parent)


def test_initialization(game):
    assert game.state == GameState.INITIALIZING

@pytest.fixture(params=[
    [('PlayerName', 'Sheeo'),
     ('StartSpot', 0)]
])
def player_option(request):
    return request.param

@pytest.fixture
def game_connection():
    return mock.create_autospec(spec=GameConnection)


def test_add_game_connection(game: Game, players, game_connection):
    game.state = GameState.LOBBY
    game_connection.player = players.hosting
    game_connection.state = GameConnectionState.connected_to_host
    game.add_game_connection(game_connection)
    assert players.hosting in game.players


def test_add_game_connection_throws_if_not_connected_to_host(game: Game, players, game_connection):
    game.state = GameState.LOBBY
    game_connection.player = players.hosting
    game_connection.state = GameConnectionState.initialized
    with pytest.raises(GameError):
        game.add_game_connection(game_connection)

    assert players.hosting not in game.players


def test_remove_game_connection(game: Game, players, game_connection):
    game.state = GameState.LOBBY
    game_connection.player = players.hosting
    game_connection.state = GameConnectionState.connected_to_host
    game.add_game_connection(game_connection)
    game.remove_game_connection(game_connection)
    assert players.hosting not in game.players


def test_game_end_when_no_more_connections(game: Game, game_connection):
    game.state = GameState.LOBBY
    game.on_game_end = mock.Mock()
    game_connection.state = GameConnectionState.connected_to_host
    game.add_game_connection(game_connection)
    game.remove_game_connection(game_connection)
    game.on_game_end.assert_any_call()


def test_game_teams_represents_active_teams(game: Game, players):
    game.state = GameState.LIVE
    players.hosting.team = 1
    players.joining.team = 2
    game._players = [players.hosting, players.joining]
    assert game.teams == {1: [players.hosting],
                          2: [players.joining]}
