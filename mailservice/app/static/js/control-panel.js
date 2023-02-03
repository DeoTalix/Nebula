function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initNewMessageForm(form){
    // Select elements
    const csrftoken = getCookie("csrftoken");
    const button = document.querySelector("#send-message-btn");
    const emailPreviewPopup = document.querySelector("#email-preview");
    const emailPreviewContent = emailPreviewPopup.querySelector("#email-preview-content");
    const emailPreviewCloseBtn = emailPreviewPopup.querySelector(".deletelink");
    const sendMessagePopup = document.querySelector("#send-message-popup");
    const formCloseBtn = form.querySelector(".deletelink");
    const mailTemplateSelect = form.querySelector("#template");
    const previewBtn = form.querySelector("#template-preview-btn");
    const loadingStatus = form.querySelector('.loading');
    const successStatus = form.querySelector('.success');
    const failureStatus = form.querySelector('.failure');
    const actionToggle = document.querySelector("#action-toggle");
    const checkBoxes = document.querySelectorAll("table#result_list tbody input[type='checkbox']");

    // Define handlers
    function handleCloseBtnClick(event) {
        sendMessagePopup.classList.remove("d-block");
    }
    function handleEmailPreviewCloseBtnClick(event) {
        emailPreviewPopup.classList.remove("d-block");
        emailPreviewContent.innerHTML = "";
    }

    function handleNewMessageFormSubmit(event) {
        event.preventDefault();

        loadingStatus.classList.add('d-block');
        
        const formData = new FormData(form);
        const formDataObject = {};
        Array.from(formData.entries()).forEach(([k, v]) => formDataObject[k] = v);
        const checkedCheckBoxes = Array.from(checkBoxes).filter(item => item.checked);
        const personIds = checkedCheckBoxes.map(item => parseInt(item.value, 10));
        // Send form data
        fetch(form.action, {
            method: 'POST',
            body: JSON.stringify({
                person_ids: personIds,
                form_data: formDataObject,
            }),
            headers: { 
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            mode: "same-origin",
        })
        .then(response => {
            return response.text();
        })
        .then(data => {
            loadingStatus.classList.remove('d-block');
            if (data.trim() == 'OK') {
                successStatus.classList.add('d-block');
                setTimeout(x => successStatus.classList.remove("d-block"), 3000);
                form.reset();
            } else {
                throw new Error(data ? data : 'Form submission failed and no error message returned from: ' + form.action);
            }
        })
        .catch(error => {
            console.error(error);
            failureStatus.innerHTML = error;
            failureStatus.classList.add("d-block");
            setTimeout(x => {
                failureStatus.classList.remove("d-block");
                failureStatus.innerHTML = "";
            }, 3000);
        });
    }

    function getMailTemplateList() {
        // Send post request to get a list of existing tempates (names)
        fetch(mailTemplateListUrl, {
            method: 'POST',
            body: {},
            headers: { 
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            mode: "same-origin",
        })
        .then(response => {
            if (response.ok)
                return response.json();
            else
                throw new Error(`Bad response status (${response.status})`);
        })
        .then(json => {
            const templates = JSON.parse(json);

            templates.forEach(item => {
                const option = document.createElement("option");
                option.value = item;
                option.innerText = item;
                mailTemplateSelect.append(option);
            });
        })
        .catch(error => console.error(error));
    }

    function handlePreviewBtnClick(event) {
        // Send post request to get a rendered template html
        const message = form.querySelector("#message").value;
        const template = form.querySelector("#template").value;

        fetch(templatePreviewUrl, {
            method: 'POST',
            body: JSON.stringify({
                message: message,
                template: template,
            }),
            headers: { 
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            mode: "same-origin",
        })
        .then(response => {
            if (response.ok)
                return response.text();
            else
                throw new Error(`Bad response status (${response.status})`);
        })
        .then(html => {
            const shadow = emailPreviewContent.shadowRoot || emailPreviewContent.attachShadow({mode: 'open'});
            
            shadow.innerHTML = html;
            emailPreviewPopup.classList.add("d-block");
        })
        .catch(error => {
            console.error(error);
            failureStatus.innerHTML = error;
            failureStatus.classList.add("d-block");
            setTimeout(x => {
                failureStatus.classList.remove("d-block");
                failureStatus.innerHTML = "";
            }, 3000);
        });
    }

    function handleActionToggleClick(event) {
        checkBoxes.forEach(item => { item.checked = event.target.checked; });
        if (event.target.checked === true)
            button.classList.add("active");
        else
            button.classList.remove("active");
    }

    function handleCheckBoxClick(event) {
        const checkedCheckBoxes = Array.from(checkBoxes).filter(item => item.checked);
        if (checkedCheckBoxes.length > 0)
            button.classList.add("active");
        else
            button.classList.remove("active");
    }

    function handleSendMessageBtnClick(event) {
        if (event.target.classList.contains("active") === false) {
            alert("Выберите хотя бы одного получателя сообщения");
            return;
        }
        sendMessagePopup.classList.add("d-block");
    }

    // Add event listeners
    formCloseBtn.addEventListener("click", handleCloseBtnClick);
    emailPreviewCloseBtn.addEventListener("click", handleEmailPreviewCloseBtnClick);
    previewBtn.addEventListener("click", handlePreviewBtnClick);
    form.addEventListener("submit", handleNewMessageFormSubmit);
    checkBoxes.forEach(checkBox => {
        checkBox.addEventListener("click", handleCheckBoxClick);
    }); 
    actionToggle.addEventListener("click", handleActionToggleClick);
    button.addEventListener("click", handleSendMessageBtnClick);

    // Call section
    getMailTemplateList();
}

window.addEventListener("load", event => {
    const newMessageForm = document.forms.newMessageForm;
    
    if (newMessageForm) 
        initNewMessageForm(newMessageForm);
});