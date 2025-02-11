document.addEventListener("DOMContentLoaded", function () {
  const goalInput = document.getElementById("saving-goal");
  const saveButton = document.getElementById("save-goal");
  const goalAmountSpan = document.getElementById("goal-amount");
  const progressBar = document.getElementById("progress-bar");
  const currentSaving = 5000000; // Giá trị tiết kiệm hiện tại
  let savingsGoal = 10000000; // Mục tiêu mặc định

  const notReachedMsg = document.getElementById("not-reached");
  const reachedMsg = document.getElementById("reached");

  /** 📌 Hàm định dạng số có dấu phẩy */
  function formatCurrency(value) {
    return value.toLocaleString("en-US") + " VND"; // Định dạng chuẩn
  }

  /** 📌 Hàm cập nhật giao diện */
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
    progressBar.style.width = `${Math.min(progress, 100)}%`;
    progressBar.textContent = `${Math.min(progress, 100).toFixed(0)}%`;
  }

  /** 📌 Cập nhật tiến trình ngay khi nhập số */
  goalInput.addEventListener("input", function () {
    let rawValue = goalInput.value.replace(/,/g, "").replace(/\D/g, ""); // Loại bỏ dấu `,` và ký tự không phải số
    if (rawValue === "") {
      savingsGoal = 1; // Tránh chia cho 0
    } else {
      savingsGoal = parseInt(rawValue, 10);
    }

    goalInput.value = parseInt(rawValue, 10).toLocaleString("en-US"); // Hiển thị số có dấu `,`
    goalAmountSpan.textContent = formatCurrency(savingsGoal); // Cập nhật số mục tiêu ngay lập tức
    updateDisplay(); // Cập nhật tiến trình ngay
  });

  /** 📌 Xử lý khi nhấn "Save Goal" */
  saveButton.addEventListener("click", function () {
    alert("✅ Mục tiêu tiết kiệm đã được lưu!");
  });

  updateDisplay(); // Chạy khi trang tải xong
});
