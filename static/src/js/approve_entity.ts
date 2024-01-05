import { initFlowbite } from 'flowbite';
import 'flowbite'
import htmx from 'htmx.org'

const form_id = "approvals-form"

document.addEventListener("htmx:afterRequest",(evt)=>{
    if(evt.detail.target.id === form_id){
        // Reinitialize flowbite after htmx request
        // so the data attributes can work again after the html
        // being replaced by htmx
        initFlowbite()

        // Same thing goes for any other event listeners in the table
        setupForm()
    }
})

/* Checks or unchecks all of the checkboxes of the table */
function setupForm(){
    const form = document.querySelector(`#${form_id}`) as HTMLFormElement | null

    form?.elements["select_all"].addEventListener("change", (evt) => {
        const checkboxes = form?.querySelectorAll("input[type=checkbox]")

        checkboxes.forEach((checkbox) => {
            if(evt.target.checked){
                checkbox.setAttribute("checked", "")
            }else{
                checkbox.removeAttribute("checked")
            }
        })
    })
}

document.addEventListener("DOMContentLoaded", (evt) => {
    setupForm()
})


// Used to prevent setting the onclick attribute multiple times
let prevApprovalId: number

/** Adds events listeners to the modal buttons */
function addEventListerners(approvalId: number, approveBtn: HTMLButtonElement | null, rejectBtn: HTMLButtonElement | null){

    // If we are still showing the same approval, we don't need to add the event listeners again
    if (prevApprovalId === approvalId) {
        return
    }

    // Add or replace the onclick event listener, we need to use setAttribute because
    // addEventListener can add an unlimited amount of event listeners, thus causing multiple
    // executions of the approveReject function
    approveBtn?.setAttribute(
        "onclick",
        `approveReject(${approvalId}, 'APPROVE')`,
    )

    rejectBtn?.setAttribute(
        "onclick",
        `approveReject(${approvalId}, 'REJECT')`,
    )

    // Update the previous approval id
    prevApprovalId = approvalId

}

/**
Sets the content of the modal for two types of files

Needed to set openModal on the window object because vite wraps this script
into a module, which means that the function is not available in the global scope
and can't be used on the onclick attribute of an element
*/
window.openModal = (approvalId: number, user_name: string, user_type: string, file_type: string, file_url: string) =>{


    const approveBtn = document.querySelector("#approve-btn") as HTMLButtonElement | null
    const rejectBtn = document.querySelector("#reject-btn") as HTMLButtonElement | null
    console.log(approvalId, user_name, user_type, file_type, file_url)

    // Add event listeners to the buttons
    addEventListerners(approvalId, approveBtn, rejectBtn)

    const modalElement = document.querySelector('#default-modal');
    // If the modal element is not found we can't continue the excution
    if (!modalElement) {
      throw new Error('Could not find modal element');
    }

    const userNameElement = modalElement.querySelector("#user_name")
    const fileViewerElement  = modalElement.querySelector("#file_viewer")
    const userTypeElement = modalElement.querySelector("#user_type")

    if(!userNameElement || !fileViewerElement || !userTypeElement){
        throw new Error('Could not find user_name or file_viewer element');
    }

    userNameElement.innerHTML = user_name
    userTypeElement.innerHTML = user_type

    // Provide a link to download the file, if it is PDF
    // PDF can't be embedded because of X-Frame-Options: DENY header
    if(file_type === "pdf"){
        const template = document.querySelector("#pdf_template") as HTMLTemplateElement

        if(!template){
            console.error("pdf template element not found")
            return
        }
        // Use an html template element to not create the element
        // structure from scratch
        const pdfMessage = template.content.cloneNode(true)
        const anchor = pdfMessage.querySelector("a")
        anchor.setAttribute("href", file_url)

        fileViewerElement.replaceChildren(pdfMessage)
    // Display an image
    } else if(file_type === "image"){
        const imgElement = document.createElement("img")

        imgElement.src = file_url

        // Insert img element in fileViewerElement
        fileViewerElement.replaceChildren(imgElement)
    } else {

        const message = document.createElement("p")
        message.innerHTML = `La extensión de archivo ${file_type} no se puede mostrar`
    }
}

/** Approves or rejects a register approval */
window.approveReject = (approvalId: number, action: "APPROVE" | "REJECT") => {

    let form = document.querySelector(`#${form_id}`) as HTMLFormElement | null

    const checkboxId = form?.querySelector(`input[value="${approvalId}"]`) as HTMLInputElement
    if(!checkboxId){
        throw new Error(`Could not find checkbox element for id ${approvalId}`);
    }
    checkboxId.setAttribute("checked", 'true')

    // Refetch the form again
    form = document.querySelector(`#${form_id}`) as HTMLFormElement | null

    if(!form?.checkValidity()){
        console.error("form is not valid")
        return
    }

    const values = htmx.values(form, "post")

    if (!values) {
      throw new Error('Could not find values');
    }

    values["action"] = action

    // Think i should return this promise
    htmx.ajax("POST","", {
        values: values,
        target: `#${form_id}`,
        swap: "outerHTML",
    }).then(()=>{
        console.log(`${action} ${approvalId}`)
    })
}
