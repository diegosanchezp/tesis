# UI tests

# Register view
url: /register/

## Profile selector

**Expected behavior**
- [ ] Changes the register button text to what the selector has currently select
- [ ] Only one button has the checkmark
- [ ] Saves  "mentor", "estudiante", "empresa"  to localstorage using [Alpine persist](https://alpinejs.dev/plugins/persist)

## Carrera selector

**Expected behavior**
- [ ] Saves selected carreer to local storage.
- [ ] When performing a search it updates the list according to the search key.
     - [ ] If the search key is empty it shows all the carreers.
     - [ ] If the search did not match anything show appropriate message.
- [ ] Shows a loading spinner When performing a search.
- [ ] If a carreer was previously selected.
    - [ ] Shows save button
    - [ ] Shows message `carreer` was selected".
    - [ ] Marks as checked the corresponding radio input
- [ ] Shows save button when a carreer is selected.

# Select Specialization view

**Expected behavior**
- [ ] Fetches the specializations of a carreer
- [ ] Can search between specializations
- [ ] Saves selected specialization to localstorage
- [ ] Restores selected specialization
- [ ] Makes proper url to next views.
Error checks:
- Displays red text if selected career doesn't matches the carreer that was provided in the URL path

# Select theme view
- [ ] Themes are paginated.
- [ ] If previous themes were selected, it restores them from localstorage.
Error checks:
- [ ] Mentors can't choose themes: displays a message if selected profile is a mentor

# Complete profile view

**Expected behavior**
- [ ] When the form is submitted,
    - [ ] It creates entity Student or Mentor in the database.
    - [ ] Redirects to the success view.
- [ ] If an error message is returned file fields are not reset.
Error checks:
- [ ] Shows red text if any of the query parameters `carreer` or `profile` are empty.
- [ ] If user with an email already exists, shows error message in red text.

**Expected behavior**
# Mentor Add Experience view
- [ ] All job descriptions are saved to local storage.
- [ ] Can delete a job description.
