"""Tests for projects and tasks CRUD."""


class TestProjects:
    def test_create_project(self, authorized_client):
        resp = authorized_client.post("/api/projects", json={
            "name": "My Project",
            "description": "Description here",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "My Project"
        assert data["owner_id"] is not None

    def test_list_projects(self, authorized_client, test_project):
        resp = authorized_client.get("/api/projects")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_project(self, authorized_client, test_project):
        project_id = test_project["id"]
        resp = authorized_client.get(f"/api/projects/{project_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == project_id

    def test_update_project(self, authorized_client, test_project):
        project_id = test_project["id"]
        resp = authorized_client.put(f"/api/projects/{project_id}", json={
            "name": "Updated Name",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_delete_project(self, authorized_client, test_project):
        project_id = test_project["id"]
        resp = authorized_client.delete(f"/api/projects/{project_id}")
        assert resp.status_code == 200

    def test_project_members(self, authorized_client, test_project):
        project_id = test_project["id"]
        resp = authorized_client.get(f"/api/projects/{project_id}/members")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1  # owner is always a member


class TestTasks:
    def test_create_task(self, authorized_client, test_project):
        resp = authorized_client.post("/api/tasks", json={
            "title": "New Task",
            "description": "Task description",
            "project_id": test_project["id"],
            "priority": "high",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "New Task"
        assert data["project_id"] == test_project["id"]

    def test_list_tasks(self, authorized_client, test_project):
        # Create a task first
        authorized_client.post("/api/tasks", json={
            "title": "Task to list",
            "project_id": test_project["id"],
        })
        resp = authorized_client.get(f"/api/tasks/project/{test_project['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_update_task(self, authorized_client, test_project):
        resp = authorized_client.post("/api/tasks", json={
            "title": "Update me",
            "project_id": test_project["id"],
        })
        task_id = resp.json()["id"]
        resp = authorized_client.put(f"/api/tasks/{task_id}", json={
            "title": "Updated title",
            "status": "in_progress",
        })
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated title"
        assert resp.json()["status"] == "in_progress"

    def test_delete_task(self, authorized_client, test_project):
        resp = authorized_client.post("/api/tasks", json={
            "title": "Delete me",
            "project_id": test_project["id"],
        })
        task_id = resp.json()["id"]
        resp = authorized_client.delete(f"/api/tasks/{task_id}")
        assert resp.status_code == 200

    def test_my_tasks(self, authorized_client, test_project):
        authorized_client.post("/api/tasks", json={
            "title": "Assigned to me",
            "project_id": test_project["id"],
            "assignee_id": authorized_client.get("/api/auth/me").json()["id"],
        })
        resp = authorized_client.get("/api/tasks/mine")
        assert resp.status_code == 200

    def test_task_position_update(self, authorized_client, test_project):
        """Test that position can be updated (for drag & drop)."""
        resp = authorized_client.post("/api/tasks", json={
            "title": "Position task",
            "project_id": test_project["id"],
        })
        task_id = resp.json()["id"]
        resp = authorized_client.put(f"/api/tasks/{task_id}", json={"position": 5})
        assert resp.status_code == 200
        assert resp.json()["position"] == 5


class TestComments:
    def test_create_comment(self, authorized_client, test_project):
        task_resp = authorized_client.post("/api/tasks", json={
            "title": "Comment task",
            "project_id": test_project["id"],
        })
        task_id = task_resp.json()["id"]
        resp = authorized_client.post("/api/comments", json={
            "content": "This is a comment",
            "task_id": task_id,
        })
        assert resp.status_code == 200
        assert resp.json()["content"] == "This is a comment"

    def test_list_comments(self, authorized_client, test_project):
        task_resp = authorized_client.post("/api/tasks", json={
            "title": "List comments task",
            "project_id": test_project["id"],
        })
        task_id = task_resp.json()["id"]
        authorized_client.post("/api/comments", json={
            "content": "Comment 1",
            "task_id": task_id,
        })
        resp = authorized_client.get(f"/api/comments/task/{task_id}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_delete_comment(self, authorized_client, test_project):
        task_resp = authorized_client.post("/api/tasks", json={
            "title": "Delete comment task",
            "project_id": test_project["id"],
        })
        task_id = task_resp.json()["id"]
        comment_resp = authorized_client.post("/api/comments", json={
            "content": "Delete me",
            "task_id": task_id,
        })
        comment_id = comment_resp.json()["id"]
        resp = authorized_client.delete(f"/api/comments/{comment_id}")
        assert resp.status_code == 200
