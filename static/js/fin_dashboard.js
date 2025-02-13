document.addEventListener("DOMContentLoaded", function () {
  const goalInput = document.getElementById("saving-goal");
  const saveButton = document.getElementById("save-goal");
  const goalAmountSpan = document.getElementById("goal-amount");
  const progressBar = document.getElementById("progress-bar");
  const notReachedMsg = document.getElementById("not-reached");
  const reachedMsg = document.getElementById("reached");

  let currentSaving = 5000000; // Giá trị tiết kiệm hiện tại
  let savingsGoal = 10000000; // Mặc định, sẽ được cập nhật từ back-end

  /** 📌 Lấy dữ liệu từ back-end */
  async function fetchGoal() {
    try {
      let response = await fetch("/get_goal");
      let data = await response.json();
      savingsGoal = data.goal_amount;
      goalAmountSpan.textContent = formatCurrency(savingsGoal);
      updateDisplay();
    } catch (error) {
      console.error("Lỗi khi lấy mục tiêu tiết kiệm:", error);
    }
  }

  /** 📌 Hàm định dạng số */
  function formatCurrency(value) {
    return value.toLocaleString("en-US") + " VND";
  }

  /** 📌 Cập nhật UI */
  function updateDisplay() {
    let progress = (currentSaving / savingsGoal) * 100;
    progressBar.style.width = `${Math.min(progress, 100)}%`;
    progressBar.textContent = `${Math.min(progress, 100).toFixed(0)}%`;

    if (currentSaving >= savingsGoal) {
      reachedMsg.style.display = "block";
      notReachedMsg.style.display = "none";
    } else {
      reachedMsg.style.display = "none";
      notReachedMsg.style.display = "block";
    }
  }

  /** 📌 Cập nhật khi nhập số */
  goalInput.addEventListener("input", function () {
    let rawValue = goalInput.value.replace(/,/g, "").replace(/\D/g, "");
    savingsGoal = rawValue === "" ? 1 : parseInt(rawValue, 10);
    goalInput.value = savingsGoal.toLocaleString("en-US");
    goalAmountSpan.textContent = formatCurrency(savingsGoal);
    updateDisplay();
  });

  /** 📌 Lưu dữ liệu lên back-end */
  saveButton.addEventListener("click", async function () {
    try {
      let response = await fetch("/set_goal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal_amount: savingsGoal }),
      });
      let result = await response.json();
      alert(result.message);
    } catch (error) {
      console.error("Lỗi khi lưu mục tiêu:", error);
    }
  });

  fetchGoal(); // 📌 Gọi khi trang tải xong
});
