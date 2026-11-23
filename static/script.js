
const dateElement = document.getElementById("current-date");

if (dateElement) {
    dateElement.textContent = new Date().toLocaleDateString(
        "en-SG",
        {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );
}


// Task search and filtering

const searchInput = document.getElementById("searchInput");
const statusFilter = document.getElementById("statusFilter");
const priorityFilter = document.getElementById("priorityFilter");

function filterTasks() {

    const searchValue = searchInput.value.toLowerCase();
    const selectedStatus = statusFilter.value;
    const selectedPriority = priorityFilter.value;

    const taskCards = document.querySelectorAll(".task-card");

    taskCards.forEach(card => {

        const title = card.dataset.title;
        const status = card.dataset.status;
        const priority = card.dataset.priority;

        const matchesSearch = title.includes(searchValue);

        const matchesStatus =
            selectedStatus === "all" ||
            status === selectedStatus;

        const matchesPriority =
            selectedPriority === "all" ||
            priority === selectedPriority;

        if (matchesSearch && matchesStatus && matchesPriority) {
            card.style.display = "flex";
        } else {
            card.style.display = "none";
        }

    });
}

if (searchInput && statusFilter && priorityFilter) {

    searchInput.addEventListener("input", filterTasks);

    statusFilter.addEventListener("change", filterTasks);

    priorityFilter.addEventListener("change", filterTasks);

}
