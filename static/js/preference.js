
const toggles = document.querySelectorAll(".preference-toggle");
const likesInput = document.getElementById("likes-input");
const dislikesInput = document.getElementById("dislikes-input");
const saveButton = document.getElementById("save-preferences");
const status = document.getElementById("preferences-status");

// Expand and collapse the preference sections.
toggles.forEach((button) => {
    button.addEventListener("click", () => {
        const panelId = button.getAttribute("aria-controls");
        const panel = document.getElementById(panelId);
        const isExpanded =
            button.getAttribute("aria-expanded") === "true";

        button.setAttribute("aria-expanded", String(!isExpanded));
        panel.hidden = isExpanded;
    });
});

// Restore previously saved preferences on this browser.
likesInput.value = localStorage.getItem("lexLikes") || "";
dislikesInput.value = localStorage.getItem("lexDislikes") || "";

// Save preferences.
saveButton.addEventListener("click", () => {
    localStorage.setItem("lexLikes", likesInput.value.trim());
    localStorage.setItem("lexDislikes", dislikesInput.value.trim());

    status.textContent = "Your preferences have been saved!";
});
