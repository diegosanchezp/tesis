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
- [ ] Shows a loading spinner When performing a search.
- [ ] If a carreer was previously selected.
    - [ ] Shows save button
    - [ ] Shows message `carreer` was selected".
    - [ ] Marks as checked the corresponding radio input
- [ ] Shows save button when a carreer is selected.

# Specialization
- [ ] Fetches the specializations of a carreer
- [ ] Can search between specializations
- [ ] Saves selected specialization to localstorage
- [ ] Restores selected specialization
- [ ] Makes proper url to next views.
Errors
Display red text if selected carreer doesn't matches the carreer that was provided in the URL path
