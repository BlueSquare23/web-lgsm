// Marks delete_user checkbox as checked when delete_user is selected.
function checkDelFiles() {
  const deleteUser = document.getElementById('delete_user');
  const deleteFiles = document.getElementById('delete_files');
  if (deleteUser.checked) {
    deleteFiles.checked = true;
  }
}
// Marks keep_user checkbox as checked when leave game servers is selected.
function checkKeepUser() {
  const leaveFiles = document.getElementById('leave_files');
  const keepUser = document.getElementById('keep_user');
  if (leaveFiles.checked) {
    keepUser.checked = true;
  }
}
// Initial call to set the correct state on page load. Defaults to
// checkKeepUser if conf is conflicted for end user safety. Safer to
// default to keep, than delete.
document.addEventListener('DOMContentLoaded', function() {
  checkKeepUser();
});
