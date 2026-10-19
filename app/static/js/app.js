const taskList = document.getElementById("task-list");

// Calls the TaskFlow API and returns the JSON, or throws the API's error message
async function api(path, options = {}) {
    const response = await fetch(`/api${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || `Request failed (${response.status})`);
    }
    return data;
}

function renderTasks(tasks) {
    taskList.innerHTML = "";

    if (tasks.length === 0) {
        const empty = document.createElement("li");
        empty.className = "list-group-item text-muted";
        empty.textContent = "No tasks yet.";
        taskList.appendChild(empty);
        return;
    }

    for (const task of tasks) {
        const item = document.createElement("li");
        item.className = "list-group-item";
        item.dataset.taskId = task.id;

        const title = document.createElement("div");
        title.className = "fw-semibold task-title";
        title.textContent = task.title;

        const badge = document.createElement("span");
        badge.className = task.status === "completed"
            ? "badge bg-success ms-2 task-status"
            : "badge bg-secondary ms-2 task-status";
        badge.textContent = task.status;
        title.appendChild(badge);

        item.appendChild(title);

        if (task.description) {
            const description = document.createElement("div");
            description.className = "text-muted small task-description";
            description.textContent = task.description;
            item.appendChild(description);
        }
        if (task.status === "completed") {
            item.classList.add("task-completed");
        }

        const actions = document.createElement("div");
        actions.className = "mt-2 d-flex gap-2 task-actions";

        const toggleButton = document.createElement("button");
        toggleButton.type = "button";
        toggleButton.className = "btn btn-sm btn-outline-success toggle-status-btn";
        toggleButton.dataset.action = "toggle";
        toggleButton.dataset.nextStatus = task.status === "completed" ? "pending" : "completed";
        toggleButton.textContent = task.status === "completed" ? "Mark pending" : "Mark completed";
        actions.appendChild(toggleButton);

        item.appendChild(actions);
        taskList.appendChild(item);
    }
}

async function loadTasks() {
    try {
        const data = await api("/tasks");
        renderTasks(data.tasks);
    } catch (error) {
        taskList.innerHTML = "";
        const item = document.createElement("li");
        item.className = "list-group-item text-danger";
        item.textContent = `Could not load tasks: ${error.message}`;
        taskList.appendChild(item);
    }
}

loadTasks();

const taskForm = document.getElementById("task-form");
const titleInput = document.getElementById("task-title");
const descriptionInput = document.getElementById("task-description");
const formError = document.getElementById("form-error");

function showFormError(message) {
    formError.textContent = message;
    formError.classList.remove("d-none");
}

function clearFormError() {
    formError.textContent = "";
    formError.classList.add("d-none");
}

taskForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFormError();

    const description = descriptionInput.value.trim();

    try {
        await api("/tasks", {
            method: "POST",
            body: JSON.stringify({
                title: titleInput.value,
                description: description || null,
            }),
        });
        taskForm.reset();
        titleInput.focus();
        await loadTasks();
    } catch (error) {
        showFormError(error.message);
    }
});
taskList.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) {
        return;
    }

    const taskId = button.closest("li[data-task-id]").dataset.taskId;

    try {
        if (button.dataset.action === "toggle") {
            await api(`/tasks/${taskId}`, {
                method: "PATCH",
                body: JSON.stringify({ status: button.dataset.nextStatus }),
            });
        }
        await loadTasks();
    } catch (error) {
        alert(`Could not update task: ${error.message}`);
    }
});