
function openEditModal(id, source, amount) {
  document.getElementById('edit-income-id').value = id;
  document.getElementById('edit-income-name').value = source;
  document.getElementById('edit-income-amount').value = amount;
  document.getElementById('editIncomeModal').style.display = 'block';
}

function closeEditModal() {
  document.getElementById('editIncomeModal').style.display = 'none';
}









function openEditBudgetModal(id, name, amount) {
  document.getElementById('edit-budget-id').value = id;
  document.getElementById('edit-budget-name').value = name;
  document.getElementById('edit-budget-amount').value = amount;
  document.getElementById('editBudgetModal').style.display = 'block';
}

function closeEditBudgetModal() {
  document.getElementById('editBudgetModal').style.display = 'none';
}









 // Populate edit modal with current expense data
 const editExpenseModal = document.getElementById('editExpenseModal');
 editExpenseModal.addEventListener('show.bs.modal', function(event) {
     const button = event.relatedTarget;
     const expenseId = button.getAttribute('data-expense-id');
     const expenseName = button.getAttribute('data-expense-name');
     const expenseAmount = button.getAttribute('data-expense-amount');
     const expenseCategory = button.getAttribute('data-expense-category');

     document.getElementById('expenseId').value = expenseId;
     document.getElementById('expenseName').value = expenseName;
     document.getElementById('expenseAmount').value = expenseAmount;
     document.getElementById('expenseCategory').value = expenseCategory;
 });




 let budgetToDelete = null;

  function openDeleteBudgetModal(budgetId) {
    budgetToDelete = budgetId;
    document.getElementById('deleteBudgetModal').style.display = 'block';
  }

  function closeModal() {
    document.getElementById('deleteBudgetModal').style.display = 'none';
    budgetToDelete = null;
  }

  function confirmDeleteBudget() {
    if (budgetToDelete) {
      fetch(`/delete_budget/${budgetToDelete}`, { method: 'POST' })
        .then(response => {
          closeModal();
          if (response.ok) {
            window.location.reload();
          } else {
            alert("Failed to delete budget");
          }
        });
    }
  }










  // Function to open delete confirmation modal
  function confirmDeleteIncome(incomeId) {
    const deleteForm = document.getElementById('deleteIncomeForm');
    deleteForm.action = `/delete_income/${incomeId}`; // Set form action dynamically
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteIncomeModal'));
    deleteModal.show();
  }
  





function confirmDeleteExpense(expenseId) {
  const deleteForm = document.getElementById('deleteExpenseForm');
  deleteForm.action = `/delete_expense/${expenseId}`; // Set form action dynamically
  const deleteModal = new bootstrap.Modal(document.getElementById('deleteExpenseModal'));
  deleteModal.show();
}











  