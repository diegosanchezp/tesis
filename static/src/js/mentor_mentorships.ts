import 'flowbite'
import htmx from 'htmx.org'
import { Modal, initFlowbite } from 'flowbite';
import { initHTMXutils } from 'js/utils/htmx'
import type { ModalOptions, ModalInterface } from 'flowbite';

initHTMXutils()

/* Get the tasks of a mentorship and put it in a modal */
window.getTasks = async (taskUrl:string) => {
    const modalTarget = "#default-modal"

    await htmx.ajax("GET", taskUrl, {
        target: modalTarget,
        swap: "outerHTML",
    })

    // Build a modal
    const modalElement = document.querySelector(modalTarget) as HTMLElement

    const modalOptions: ModalOptions = {
        closable: true,
        placement: 'bottom-right',
        onHide: (modal) => {
            console.log('modal is hidden');
        },
    }
    const modal = new Modal(modalElement,modalOptions);

    // Show the modal after we get its HTML
    modal.show()

    const closeBtn = modalElement.querySelector("#close-btn")
    const requestBtn = modalElement.querySelector("#request-btn")

    // Close the modal when X button is clicked
    closeBtn.addEventListener("click", ()=>{
        modal.hide()
    })

    requestBtn.addEventListener("click", ()=>{
        modal.hide()
    })
}
