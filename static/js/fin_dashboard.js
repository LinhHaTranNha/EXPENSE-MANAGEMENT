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

// Hiển thị input giả khi người dùng click
displayInput.addEventListener("click", function () {
  realInput.style.display = "block"; // Hiện input thật
  realInput.focus(); // Đưa focus vào input thật
  displayInput.style.display = "none"; // Ẩn input giả
});

// Khi người dùng nhập vào input thật
realInput.addEventListener("input", function () {
  const rawValue = this.value.replace(/,/g, ""); // Loại bỏ dấu phẩy
  if (!isNaN(rawValue) && rawValue !== "") {
    const formattedValue = parseInt(rawValue, 10).toLocaleString("en-US");
    displayInput.value = formattedValue; // Cập nhật input giả
  }
});

// Khi rời khỏi input thật
realInput.addEventListener("blur", function () {
  const rawValue = this.value.replace(/,/g, ""); // Loại bỏ dấu phẩy
  if (!isNaN(rawValue) && rawValue !== "") {
    const formattedValue = parseInt(rawValue, 10).toLocaleString("en-US");
    displayInput.value = formattedValue; // Hiển thị giá trị đã định dạng
  }
  this.style.display = "none"; // Ẩn input thật
  displayInput.style.display = "block"; // Hiện input giả
});

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
