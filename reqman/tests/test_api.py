import json


def test_project_api_list(api_client, sample_data):
    response = api_client.get("/api/v1/project/")
    assert response.status_code == 200
    data = response.get_json()
    assert "count" in data
    assert data["count"] >= 1
    codes = [item["project_code"] for item in data["result"]]
    assert "PRJ-101" in codes


def test_project_api_get_item(api_client, sample_data):
    project_id = sample_data["project"].id
    response = api_client.get(f"/api/v1/project/{project_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"]["project_code"] == "PRJ-101"
    assert data["result"]["name"] == "Avionics Flight System"


def test_requirement_api_list(api_client, sample_data):
    response = api_client.get("/api/v1/requirement/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 1
    req_keys = [item["req_key"] for item in data["result"]]
    assert "REQ-SYS-001" in req_keys


def test_requirement_version_api_list(api_client, sample_data):
    response = api_client.get("/api/v1/requirement_version/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 1


def test_domain_target_api_list(api_client, sample_data):
    response = api_client.get("/api/v1/domain_target/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] >= 1
    identifiers = [item["identifier"] for item in data["result"]]
    assert "HW-PMU-200" in identifiers


def test_project_api_crud_workflow(api_client, db_session):
    # 1. Create a new Project via API POST
    new_project = {
        "project_code": "PRJ-TEST-API",
        "name": "API Test Payload",
        "description": "Created via pytest REST API call",
    }
    response = api_client.post(
        "/api/v1/project/",
        data=json.dumps(new_project),
        content_type="application/json",
    )
    assert response.status_code == 201
    created_data = response.get_json()
    created_id = created_data["id"]

    # 2. Retrieve created item via GET
    get_res = api_client.get(f"/api/v1/project/{created_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["result"]["project_code"] == "PRJ-TEST-API"

    # 3. Update project via PUT
    update_payload = {"name": "API Test Payload Updated"}
    put_res = api_client.put(
        f"/api/v1/project/{created_id}",
        data=json.dumps(update_payload),
        content_type="application/json",
    )
    assert put_res.status_code == 200

    # 4. Verify update
    get_res_updated = api_client.get(f"/api/v1/project/{created_id}")
    assert get_res_updated.get_json(
    )["result"]["name"] == "API Test Payload Updated"

    # 5. Delete project via DELETE
    del_res = api_client.delete(f"/api/v1/project/{created_id}")
    assert del_res.status_code == 200

    # 6. Verify deletion
    get_res_deleted = api_client.get(f"/api/v1/project/{created_id}")
    assert get_res_deleted.status_code == 404
