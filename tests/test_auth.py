import asyncio

import pytest
from httpx import AsyncClient
from typing import Generator

from app.main import app

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_signup(async_client):
    signup_response = await async_client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "name": "testname",
        },
    )
    assert signup_response.status_code == 201


@pytest.mark.asyncio
async def test_login(async_client):
    login_response = await async_client.post(
        "/auth/login", data={"username": "test@example.com", "password": "testpassword"}
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_create_game(async_client, event_loop):
    login_response = await async_client.post(
        "/auth/login", data={"username": "test@example.com", "password": "testpassword"}
    )
    assert login_response.status_code == 200

    auth_token = login_response.json()["access_token"]
    response = await async_client.post(
        "/games/",
        json={
            "game_date": "2023-11-15",
            "home_away": "home",
            "opponent": "Los Angeles Lakers",
            "points_conceded": 108,
            "points_scored": 112,
            "season": "2023-2024",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
        follow_redirects=True,
    )
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_read_game(async_client, event_loop):
    response = await async_client.get("/games/1")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_player(async_client, event_loop):
    login_response = await async_client.post(
        "/auth/login", data={"username": "test@example.com", "password": "testpassword"}
    )
    assert login_response.status_code == 200

    auth_token = login_response.json()["access_token"]
    response = await async_client.post(
        "/players/",
        json={
            "height": 2.01,
            "jersey_number": 77,
            "name": "Luka Dončić",
            "position": "Point Guard",
            "weight": 104
            },
        headers={"Authorization": f"Bearer {auth_token}"},
        follow_redirects=True,
    )
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_read_player(async_client, event_loop):
    response = await async_client.get("/players/1")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_stats_player_for_game(async_client, event_loop):
    response = await async_client.post(
        "/stats/games/1/players/1",
        json={
            "assists": 5,
            "blocks": 1,
            "field_goals_attempted": 15,
            "field_goals_made": 8,
            "free_throws_attempted": 5,
            "free_throws_made": 4,
            "minutes_played": 34.5,
            "personal_fouls": 3,
            "plus_minus": 12,
            "points": 25,
            "rebounds": 7,
            "stats_type": "player",
            "steals": 2,
            "three_points_attempted": 6,
            "three_points_made": 3,
            "turnovers": 2
            },
        follow_redirects=True,
    )
    assert response.status_code == 200