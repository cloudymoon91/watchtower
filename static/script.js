
function callApi(apiUrl, element) {
    // Hide all input forms
    document.querySelectorAll('.input-form').forEach(form => {
        form.style.display = 'none';
    });

    // Remove active class from all menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    // Add active class to the clicked menu item
    element.classList.add('active');

    // Show the loading spinner for the selected menu item
    const spinner = element.querySelector('.spinner-border');
    spinner.style.display = 'inline-block';

    // Fetch data from the API
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            document.getElementById('result').innerText = 'Error: ' + error;
        })
        .finally(() => {
            // Hide the loading spinner once the response is received
            spinner.style.display = 'none';
        });
}

function showInputForm(formId, element) {
    // Hide all input forms
    document.querySelectorAll('.input-form').forEach(form => {
        form.style.display = 'none';
    });

    // Remove active class from all menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to the clicked menu item
    element.classList.add('active');

    // Show the specific input form
    // Add event listener for Enter key press on input fields
    const inputField = document.getElementById(formId).querySelector('input');
    document.getElementById(formId).style.display = 'block';
    inputField.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            // Prevent the default form submission
            event.preventDefault();
            // Trigger the submit function
            const button = document.getElementById(formId).querySelector('button');
            button.click();
        }
    });
}

function submitInput(inputId, apiUrl, spinnerId) {
    const userInput = document.getElementById(inputId).value;
    const urlWithParams = `${apiUrl}/${encodeURIComponent(userInput)}`;

    // Show loading spinner for the form submit
    const loadingSpinner = document.getElementById(spinnerId);
    loadingSpinner.style.display = 'inline-block';

    fetch(urlWithParams)
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            document.getElementById('result').innerText = 'Error: ' + error;
        })
        .finally(() => {
            // Hide loading spinner once the response is received
            loadingSpinner.style.display = 'none';
        });
}

function checkEnter(event, inputId, apiUrl, spinnerId) {
    if (event.key === 'Enter') {
        submitInput(inputId, apiUrl, spinnerId);
    }
}
