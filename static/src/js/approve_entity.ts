import { initFlowbite } from 'flowbite';
import 'flowbite'
import { Modal } from 'flowbite';
import type { ModalOptions } from 'flowbite';
import htmx from 'htmx.org'

const form_id = "approvals-form"

document.addEventListener("htmx:afterRequest",(evt)=>{
    if(evt.detail.target.id === form_id){
        // Reinitialize event listeners on the table after htmx replaces them
        setupForm()
    }
})

/** Checks or unchecks all of the checkboxes of the table */
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

/**
Sets the content of the modal for two types of files

Needed to set openModal on the window object because vite wraps this script
into a module, which means that the function is not available in the global scope
and can't be used on the onclick attribute of an element
*/
window.openModal = async (approvalId: number) =>{
    const modalTarget = "#approval-modal"

    await htmx.ajax("GET", "", {
        target: `${modalTarget}`,
        values: {
            "approval_pk": approvalId,
            "action": "get_modal"
        },
        swap: "innerHTML",
    })

    const modalElement = document.querySelector(modalTarget) as HTMLElement

    const modalOptions: ModalOptions = {
        closable: true,
        placement: 'bottom-right',
    }
    const modal = new Modal(modalElement,modalOptions);

    // Show the modal after we get its HTML
    modal.show()

    const closeBtn = modalElement.querySelector("#close-btn")

    // Close the modal when X button is clicked
    closeBtn.addEventListener("click", ()=>{
        modal.hide()
    })
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
    values["modality"] = "modal"

    // Think i should return this promise
    htmx.ajax("POST","", {
        values: values,
        target: `#${form_id}`,
        swap: "outerHTML",
    }).then(()=>{
        console.log(`${action} ${approvalId}`)
    })
}
