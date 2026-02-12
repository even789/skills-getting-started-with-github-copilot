import pytest


def test_root_redirect(client):
    """Test that root redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    
    # Check structure of an activity
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_new_participant(client):
    """Test signing up a new participant"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert "newstudent@mergington.edu" in result["message"]
    assert "Chess Club" in result["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_existing_participant(client):
    """Test that signing up an already registered participant fails"""
    # michael@mergington.edu is already in Chess Club
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for a nonexistent activity"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"]


def test_unregister_participant(client):
    """Test unregistering a participant"""
    # michael@mergington.edu is in Chess Club
    response = client.post(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert "michael@mergington.edu" in result["message"]
    assert "Chess Club" in result["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_participant(client):
    """Test unregistering a participant not in the activity"""
    response = client.post(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    
    result = response.json()
    assert "detail" in result
    assert "not registered" in result["detail"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregistering from a nonexistent activity"""
    response = client.post(
        "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"]


def test_signup_at_full_capacity(client):
    """Test that signing up for a full activity fails"""
    # Basketball Team has max_participants=15 and 1 participant
    # Add 14 more to fill it up
    for i in range(14):
        client.post(
            f"/activities/Basketball%20Team/signup?email=student{i}@mergington.edu"
        )
    
    # Try to add one more (should fail)
    response = client.post(
        "/activities/Basketball%20Team/signup?email=overflow@mergington.edu"
    )
    assert response.status_code == 400


def test_get_activities_includes_all_fields(client):
    """Test that activities response includes all required fields"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_name, str)
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)
