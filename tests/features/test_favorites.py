import pytest
import ipdb
from flask import g, session
from birdy.db import get_db
from sqlalchemy import text
import json


def test_user_favorites_none_if_not_added(client, auth):
    res = auth.login()
    response = client.get('/favorites/')

    assert response.status_code == 200
    assert "Go to search to add favorite birds!" in response.data

def test_user_favorites_displayed_in_index(client, auth, app):
    res = auth.login()
    with app.app_context():
        get_db().engine.execute("INSERT INTO bird (species_code, common_name, sci_name) VALUES ('bgbrd', 'Big Bird', 'Birdus largus')")
        get_db().engine.execute("INSERT INTO user_birds (user_id, bird_id) VALUES (1, 1)")
        response = client.get('/favorites/')
        assert 'Big Bird' in response.data
        assert 'Birdus largus' in response.data
        assert 'bgbrd' in response.data

def test_user_favorites_show_page_has_recent_sightings(client, auth, app):
    res = auth.login()
    with app.app_context():
        get_db().engine.execute("INSERT INTO bird (species_code, common_name, sci_name) VALUES ('cangoo', 'Canada Goose', 'Branta canadensis')")
        get_db().engine.execute('INSERT INTO user_birds (user_id, bird_id) VALUES (1, 1)')
        response = client.get('/favorites/1')
        assert 'Canada Goose' in response.data
        assert 'Branta canadensis' in response.data
        assert 'Scientific Name' in response.data
        assert 'Observation Date' in response.data
        assert 'Location' in response.data
        assert 'How Many' in response.data

def test_user_favorites_delete_removes_bird_user_association(client, auth, app):
    res = auth.login()
    with app.app_context():
        get_db().engine.execute("INSERT INTO bird (species_code, common_name, sci_name) VALUES ('bgbrd', 'Big Bird', 'Birdus largus')")
        get_db().engine.execute('INSERT INTO user_birds (user_id, bird_id) VALUES (1, 1)')
        response = client.get('/favorites/')
        assert 'Big Bird' in response.data

        client.post('/favorites/1/delete')
        response = client.get('/favorites/')
        assert 'Big Bird' not in response.data

def test_user_favorites_search_by_location(client, auth):
    res = auth.login()
    response = client.get('/search/location')

    assert "Latitude" in response.data
    assert "Longitude" in response.data
    assert "Search" in response.data

def test_user_favorites_search_by_species(client, auth):
    res = auth.login()
    response = client.get('/search/species')

    assert 'Search for your favorite birds by species code' in response.data
    assert 'Species Code' in response.data

def test_user_favorites_does_not_store_duplicate_birds(client, auth, app):
    res = auth.login()
    with app.app_context():
        get_db().engine.execute("INSERT INTO bird (species_code, common_name, sci_name) VALUES ('bgbrd', 'Big Bird', 'Birdus largus')")
        get_db().engine.execute('INSERT INTO user_birds (user_id, bird_id) VALUES (1, 1)')
        data = {'birds': 'bgbrd/Big Bird/Birdus largus'}
        client.post(
            'api/v1/favorites', data=data
        )
        assert get_db().engine.execute("SELECT * FROM bird WHERE species_code = 'bgbrd'").fetchall().__len__() == 1
