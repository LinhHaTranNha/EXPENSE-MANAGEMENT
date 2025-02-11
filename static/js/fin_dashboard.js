document.getElementById("saving-goal").addEventListener("input", function () {
  const goalInput = parseInt(this.value) || 0; // Lấy giá trị nhập liệu
  const currentSaving = 5000000; // Giá trị tiết kiệm hiện tại
  const progressBar = document.getElementById("progress-bar");
  const goalAmountDisplay = document.getElementById("goal-amount");

  // Cập nhật mục tiêu hiển thị
  goalAmountDisplay.textContent = `${goalInput.toLocaleString()} VND`;

  // Tính phần trăm hoàn thành
  const progress = Math.min((currentSaving / goalInput) * 100, 100);

  // Cập nhật chiều rộng thanh progress
  progressBar.style.width = `${progress}%`;
  progressBar.textContent = `${Math.round(progress)}%`; // Hiển thị phần trăm trên thanh
});

// Lưu mục tiêu tiết kiệm lên cơ sở dữ liệu
document.getElementById("save-goal").addEventListener("click", function () {
  const savingGoal =
    parseInt(document.getElementById("saving-goal").value) || 0;

  if (savingGoal > 0) {
    // Gửi saving goal lên server
    fetch("/save-goal", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ goal: savingGoal }),
    })
      .then((response) => {
        if (response.ok) {
          alert("Saving goal has been saved successfully!");
        } else {
          alert("Failed to save the saving goal. Please try again.");
        }
      })
      .catch((error) => {
        console.error("Error saving goal:", error);
        alert("An error occurred while saving. Please try again.");
      });
  } else {
    alert("Please enter a valid saving goal.");
  }
});

const displayInput = document.getElementById("display-saving-goal");
const realInput = document.getElementById("real-saving-goal");
const progressBar = document.getElementById("progress-bar");
const goalAmountDisplay = document.getElementById("goal-amount");
const currentSaving = 5000000; // Giá trị tiết kiệm hiện tại

// Khi nhấn nút Save Goal
document.getElementById("save-goal").addEventListener("click", function () {
  const rawValue = realInput.value.replace(/,/g, ""); // Lấy giá trị không có dấu phẩy
  const goalValue = parseInt(rawValue, 10); // Chuyển sang số nguyên

  if (!isNaN(goalValue) && goalValue > 0) {
    // Cập nhật hiển thị mục tiêu
    goalAmountDisplay.textContent = `${goalValue.toLocaleString()} VND`;

    // Tính toán phần trăm tiến trình
    const progress = Math.min((currentSaving / goalValue) * 100, 100);
    progressBar.style.width = `${progress}%`; // Cập nhật thanh tiến trình
    progressBar.textContent = `${Math.round(progress)}%`; // Hiển thị phần trăm trên thanh

    alert("Saving goal has been saved successfully!");
  } else {
    alert("Please enter a valid saving goal.");
  }
});

// GOAL

document.addEventListener("DOMContentLoaded", function () {
  const goalInput = document.getElementById("saving-goal");
  const saveButton = document.getElementById("save-goal");
  const goalAmountSpan = document.getElementById("goal-amount");
  const progressBar = document.getElementById("progress-bar");
  const currentSaving = 5000000; // Giá trị tiết kiệm hiện tại
  let savingsGoal = 10000000; // Mục tiêu mặc định

  const notReachedMsg = document.getElementById("not-reached");
  const reachedMsg = document.getElementById("reached");

  function updateDisplay() {
    console.log(`Current Saving: ${currentSaving}, Goal: ${savingsGoal}`);

    if (currentSaving >= savingsGoal) {
      reachedMsg.style.display = "block";
      notReachedMsg.style.display = "none";
    } else {
      reachedMsg.style.display = "none";
      notReachedMsg.style.display = "block";
    }

    let progress = (currentSaving / savingsGoal) * 100;
    progressBar.style.width = progress + "%";
    progressBar.textContent = `${Math.min(progress, 100).toFixed(0)}%`;
  }

  saveButton.addEventListener("click", function () {
    let userGoal = parseInt(goalInput.value.replace(/\D/g, ""), 10);
    if (!isNaN(userGoal) && userGoal > 0) {
      savingsGoal = userGoal;
      goalAmountSpan.textContent = userGoal.toLocaleString("en-US") + " VND";
      updateDisplay();
    }
  });

  updateDisplay();
});

// END GOAL
